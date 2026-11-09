"""Write a Word copy of a UTF-8 TXT/MD manuscript using only Python 3.9+.
Usage: python make_word.py SOURCE.txt PLAN.json
For existing Word documents use the copy-and-edit route in WORKFLOW.md.
"""
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote as urlquote
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
C = "http://schemas.openxmlformats.org/package/2006/content-types"
XML = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("w", W)
ET.register_namespace("r", R)


def word(parent, tag):
    return ET.SubElement(parent, f"{{{W}}}{tag}")


def add_text(parent, value):
    run = word(parent, "r")
    parts = value.split("\t")
    for i, part in enumerate(parts):
        if i:
            word(run, "tab")
        text = word(run, "t")
        text.set(f"{{{XML}}}space", "preserve")
        text.text = part


def package(source, plan):
    raw = source.read_bytes()
    if plan["source_sha256"].lower() != hashlib.sha256(raw).hexdigest():
        raise ValueError("原稿已變動，請重新讀取並核對。")
    # Literal text lines, including blank lines and Markdown characters, are retained.
    lines = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    refs, claims = plan["references"], plan["claims"]
    used, seen_dois = set(), set()
    marks = [[] for _ in lines]
    for claim in claims:
        quote, ids = claim["sentence"], claim["refs"]
        if not quote or not ids or len(set(ids)) != len(ids):
            raise ValueError("引用必須有完整原句與不重複的文獻編號。")
        if any(type(n) is not int or not 1 <= n <= len(refs) for n in ids):
            raise ValueError("引用編號沒有對應書目。")
        positions = [(i, text.index(quote) + len(quote)) for i, text in enumerate(lines)
                     if quote in text and ("line" not in claim or claim["line"] == i + 1)]
        if len(positions) != 1 or lines[positions[0][0]].count(quote) != 1:
            raise ValueError("原句定位不唯一；重讀原稿，可用 line 指定一開始算的行號。")
        i, end = positions[0]
        if any(pos == end for pos, _ in marks[i]):
            raise ValueError("同一句的編號請合併為一組。")
        marks[i].append((end, "".join(f"[{n}]" for n in ids)))
        used.update(ids)
    if used != set(range(1, len(refs) + 1)):
        raise ValueError("每筆書目都須對應正文。")
    document = ET.Element(f"{{{W}}}document")
    body = word(document, "body")
    def paragraph(value):
        add_text(word(body, "p"), value)
    for text, inserts in zip(lines, marks):
        for pos, mark in sorted(inserts, reverse=True):
            text = text[:pos] + mark + text[pos:]
        paragraph(text)
    paragraph("參考文獻")
    rels = ET.Element("Relationships", xmlns=P)
    for n, ref in enumerate(refs, 1):
        doi = ref["doi"].strip()
        if not re.fullmatch(r"10\.\d{4,9}/[^\s?#]+", doi, re.I) or doi.casefold() in seen_dois:
            raise ValueError("DOI 格式有誤或重複。")
        seen_dois.add(doi.casefold())
        if not ref["bibliography"].strip() or not ref["support"].strip():
            raise ValueError("書目和支持依據不可空白。")
        paragraph(f"[{n}] {ref['bibliography']}")
        url = "https://doi.org/" + urlquote(doi, safe="/:;()._-")
        rid = f"rId{n}"
        ET.SubElement(rels, "Relationship", Id=rid, Type=R+"/hyperlink", Target=url, TargetMode="External")
        link = word(word(body, "p"), "hyperlink")
        link.set(f"{{{R}}}id", rid)
        add_text(link, url)
        paragraph(ref["support"])
    word(body, "sectPr")
    types = ET.Element("Types", xmlns=C)
    ET.SubElement(types, "Default", Extension="rels", ContentType="application/vnd.openxmlformats-package.relationships+xml")
    ET.SubElement(types, "Override", PartName="/word/document.xml", ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml")
    root_rels = ET.Element("Relationships", xmlns=P)
    ET.SubElement(root_rels, "Relationship", Id="rId1", Type=R+"/officeDocument", Target="word/document.xml")
    parts = {"[Content_Types].xml": types, "_rels/.rels": root_rels, "word/document.xml": document,
             "word/_rels/document.xml.rels": rels}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, node in parts.items():
            archive.writestr(name, ET.tostring(node, encoding="utf-8", xml_declaration=True))
    return output.getvalue(), lines, marks


def verify(data, lines, marks, references):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        paragraphs = root.findall(f"{{{W}}}body/{{{W}}}p")
        def read(p):
            return "".join((e.text or "") if e.tag == f"{{{W}}}t" else "\t"
                           for e in p.iter() if e.tag in (f"{{{W}}}t", f"{{{W}}}tab"))
        if len(paragraphs) <= len(lines) or read(paragraphs[len(lines)]) != "參考文獻":
            raise ValueError("Word 段落數不符。")
        for i, line in enumerate(lines):
            result = read(paragraphs[i])
            for pos, mark in sorted(marks[i]):
                if result[pos:pos+len(mark)] != mark:
                    raise ValueError("Word 引用位置不符。")
                result = result[:pos]+result[pos+len(mark):]
            if line != result:
                raise ValueError("Word 正文和原稿不符。")
        # Check the saved relationships and the bibliography against the same verified plan.
        for part in z.namelist():
            if part.endswith((".xml", ".rels")):
                ET.fromstring(z.read(part))
        relationships = ET.fromstring(z.read("word/_rels/document.xml.rels"))
        targets = {rel.get("Id"): rel for rel in relationships}
        if len(targets) != len(relationships) or len(targets) != len(references):
            raise ValueError("Word 超連結關係數目或編號不符。")
        entries = paragraphs[len(lines) + 1:]
        if len(entries) != len(references) * 3:
            raise ValueError("Word 書目筆數不符。")
        for index, ref in enumerate(references):
            n = index + 1
            bib, address, reasoning = entries[index*3:index*3 + 3]
            expected_url = "https://doi.org/" + urlquote(ref["doi"].strip(), safe="/:;()._-")
            link = address.find(f"{{{W}}}hyperlink")
            rel = None if link is None else targets.get(link.get(f"{{{R}}}id"))
            if (read(bib) != f"[{n}] {ref['bibliography']}" or read(reasoning) != ref["support"]
                    or read(address) != expected_url or rel is None
                    or rel.get("TargetMode") != "External" or rel.get("Type") != R+"/hyperlink"
                    or rel.get("Target") != expected_url):
                raise ValueError("Word 的引用、書目、佐證或 DOI 超連結不符。")
        if z.testzip() is not None:
            raise ValueError("Word 壓縮檔有損。")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--inspect":
        path = Path(sys.argv[2])
        if path.suffix.lower() not in (".txt", ".md"):
            raise ValueError("只支援 TXT/MD。")
        print(hashlib.sha256(path.read_bytes()).hexdigest())
        return
    if len(sys.argv) != 3:
        raise ValueError("用法：python make_word.py 原稿.txt 查核結果.json")
    source = Path(sys.argv[1])
    if source.suffix.lower() not in (".txt", ".md"):
        raise ValueError("本工具只收 UTF-8 TXT/MD，Word 原稿請依 WORKFLOW.md 局部編輯副本。")
    plan = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8-sig"))
    data, lines, marks = package(source, plan)
    verify(data, lines, marks, plan["references"])
    for count in range(1, 10001):
        suffix = "" if count == 1 else f"_{count}"
        path = source.with_name(source.stem + "_文獻版" + suffix + ".docx")
        try:
            with path.open("xb") as f:
                f.write(data)
        except FileExistsError:
            continue
        verify(path.read_bytes(), lines, marks, plan["references"])
        if hashlib.sha256(source.read_bytes()).hexdigest() != plan["source_sha256"].lower():
            raise ValueError("儲存時原稿已有變動，請重新查核。")
        print(str(path))
        return
    raise ValueError("輸出檔名均已存在。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        sys.exit(str(error))
