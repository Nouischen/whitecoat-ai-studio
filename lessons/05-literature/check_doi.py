#!/usr/bin/env python3
"""Optional public-metadata helper (Python 3.9+, standard library only).
Usage: python check_doi.py DOI
Exit 0: metadata comparison completed, NOT approval to cite.
Exit 1: missing/uncertain data, notices, mismatch, or network failure.
Exit 2: invalid usage. Exit 130: interrupted.
No student files, credentials, API keys, email, or personal search terms are read.
Only a supplied DOI, explicit --search keywords, and public PMIDs are sent to fixed APIs.
Proxies and redirects are disabled. No publisher/DOI resolver is opened.
API references:
https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/
https://www.ncbi.nlm.nih.gov/books/NBK25499/
"""
import html
import json
import queue
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

CROSSREF = "https://api.crossref.org/works"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
REQUEST_TIMEOUT = 8
TOTAL_TIMEOUT = 45
MAX_BYTES = 2 * 1024 * 1024
MAX_PMIDS = 10
DOI_RE = re.compile(r"10\.[0-9]{4,9}/[-A-Za-z0-9._;()/:+<>]+", re.ASCII)


class LookupProblem(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LookupProblem("redirect refused; destination not requested")


def clean(value):
    # Remove markup and terminal control characters from untrusted metadata.
    value = re.sub(r"<[^>]*>", "", str(value))
    value = html.unescape(value)
    return " ".join("".join(
        c if not unicodedata.category(c).startswith("C") else " "
        for c in value
    ).split())


def norm(value):
    return "".join(c for c in clean(value).casefold() if c.isalnum())


def text(node, path):
    element = node.find(path)
    return clean("".join(element.itertext())) if element is not None else ""


def request(opener, url, xml=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": "StudentDOICheck/1.0",
        "Accept": "application/xml" if xml else "application/json",
    })
    try:
        with opener.open(req, timeout=REQUEST_TIMEOUT) as response:
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise LookupProblem("response exceeded size limit")
        if xml:
            # ElementTree does not fetch external DTDs. Reject entity definitions.
            if b"<!ENTITY" in data.upper():
                raise LookupProblem("XML entity definitions refused")
            root = ET.fromstring(data)
            if root.find(".//ERROR") is not None:
                raise LookupProblem("PubMed returned an API error")
            return root
        return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise LookupProblem("HTTP " + str(exc.code)) from None
    except (urllib.error.URLError, OSError, ValueError, ET.ParseError):
        raise LookupProblem("network, TLS, timeout, or response parsing failure") from None


def first(values):
    return clean(values[0]) if isinstance(values, list) and values else ""


def crossref_record(work):
    authors = work.get("author") or []
    names = [clean(a.get("name") or " ".join(
        filter(None, [a.get("given"), a.get("family")])
    )) for a in authors]
    years = []
    for key in ("published", "published-print", "published-online", "issued"):
        parts = (work.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            years.append(str(parts[0][0]))
    return {
        "Authors": "; ".join(names),
        "Title": first(work.get("title")),
        "Journal": first(work.get("container-title")),
        "Year": "/".join(dict.fromkeys(years)),
        "DOI": clean(work.get("DOI", "")),
        "Type": clean(work.get("type", "")),
    }


def pubmed_record(article):
    record = article.find("./MedlineCitation/Article")
    if record is None:
        raise LookupProblem("PubMed article metadata missing")
    names = []
    for author in record.findall("./AuthorList/Author"):
        names.append(text(author, "CollectiveName") or " ".join(filter(None, [
            text(author, "ForeName") or text(author, "Initials"),
            text(author, "LastName"),
        ])))
    years = []
    date = record.find("./Journal/JournalIssue/PubDate")
    if date is not None:
        year = text(date, "Year") or text(date, "MedlineDate")
        years.extend(re.findall(r"\b[12][0-9]{3}\b", year))
    for date in record.findall("./ArticleDate"):
        year = text(date, "Year")
        if year:
            years.append(year)
    dois = [text(e, ".").casefold() for e in
            article.findall("./PubmedData/ArticleIdList/ArticleId")
            if e.get("IdType", "").casefold() == "doi"]
    return {
        "Authors": "; ".join(names),
        "Title": text(record, "ArticleTitle"),
        "Journal": text(record, "Journal/Title"),
        "Year": "/".join(dict.fromkeys(years)),
        "DOI": "; ".join(dois),
        "PMID": text(article, "MedlineCitation/PMID"),
        "Type": "; ".join(text(e, ".") for e in
                          record.findall("./PublicationTypeList/PublicationType")),
    }, dois


def lookup(doi):
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), NoRedirect()
    )
    lines = ["DOI: " + doi]
    warnings = []
    records = {}
    notice_count = 0

    def show(source, record):
        records[source] = record
        lines.append("\n[" + source + "]")
        for key, value in record.items():
            lines.append(key + ": " + (value or "UNKNOWN / missing"))
        for key in ("Authors", "Title", "Journal", "Year", "DOI", "Type"):
            if not record.get(key):
                warnings.append(source + ": missing " + key)

    try:
        payload = request(opener, CROSSREF + "/" + urllib.parse.quote(doi, safe=""))
        work = payload["message"]
        if payload.get("status") != "ok" or not isinstance(work, dict):
            raise LookupProblem("unexpected Crossref response")
        show("Crossref", crossref_record(work))
        if work.get("DOI", "").casefold() != doi:
            warnings.append("Crossref DOI does not match input")
        # update-to describes this item as a notice about another item.
        # updated-by and the reverse updates filter cover notices about this item.
        for key in ("update-to", "updated-by"):
            for update in work.get(key) or []:
                notice_count += 1
                warnings.append("Crossref " + key + ": " + clean(
                    json.dumps(update, ensure_ascii=False)))
        for kind, relations in (work.get("relation") or {}).items():
            if re.search(r"retract|correct|concern|withdraw|update", kind, re.I):
                notice_count += 1
                warnings.append("Crossref relation " + clean(kind) + ": " +
                                clean(json.dumps(relations, ensure_ascii=False)))
        for assertion in work.get("assertion") or []:
            summary = clean(json.dumps(assertion, ensure_ascii=False))
            if re.search(r"retract|withdraw|correct|errat|concern|change|update",
                         summary, re.I):
                notice_count += 1
                warnings.append("Crossref assertion (review manually): " + summary)
        if re.search(r"retract|withdraw|correction|erratum|concern",
                     records["Crossref"]["Title"], re.I):
            notice_count += 1
            warnings.append("Crossref title suggests a notice; inspect publisher page")
    except (LookupProblem, KeyError, TypeError, AttributeError, IndexError) as exc:
        warnings.append("Crossref UNKNOWN: " + clean(str(exc)))

    try:
        url = CROSSREF + "?" + urllib.parse.urlencode({
            "filter": "updates:" + doi, "rows": 20,
        })
        result = request(opener, url)["message"]
        items = result["items"]
        total = int(result["total-results"])
        if not isinstance(items, list) or total < len(items):
            raise LookupProblem("unexpected Crossref update results")
        lines.append("\nCrossref reverse-update records: " + str(total))
        if total > len(items):
            warnings.append("Crossref update results truncated; review manually")
        for item in items:
            notice_count += 1
            warnings.append("Crossref notice/update: " + clean(item.get("DOI", "")) +
                            " | " + first(item.get("title")) +
                            " | " + clean(json.dumps(item.get("update-to", []))))
    except (LookupProblem, KeyError, TypeError, ValueError, AttributeError) as exc:
        warnings.append("Crossref notice search UNKNOWN: " + clean(str(exc)))

    try:
        url = EUTILS + "esearch.fcgi?" + urllib.parse.urlencode({
            "db": "pubmed", "term": '"' + doi + '"[AID]',
            "retmode": "json", "retmax": MAX_PMIDS,
        })
        result = request(opener, url)["esearchresult"]
        if result.get("errorlist") or result.get("warninglist"):
            warnings.append("PubMed search reported warnings/errors")
        count = int(result["count"])
        ids = result["idlist"]
        if (not isinstance(ids, list) or count < 0 or count < len(ids) or
                any(not isinstance(i, str) or not i.isdigit() for i in ids)):
            raise LookupProblem("invalid PubMed identifiers")
        if count == 0:
            warnings.append("PubMed NOT_FOUND: absence is not proof of safety; "
                            "non-biomedical work may not be indexed")
            lines.append("\nPubMed: no PMID found")
        elif count != 1 or len(ids) != 1:
            warnings.append("PubMed identity AMBIGUOUS/incomplete: " + str(count) +
                            " search results; no PMID accepted")
            lines.append("\nPubMed candidate PMIDs (unverified): " + ", ".join(ids))
        else:
            time.sleep(0.35)  # Stay below 3 Eutilities requests/second, no API key.
            root = request(opener, EUTILS + "efetch.fcgi?" +
                           urllib.parse.urlencode({
                               "db": "pubmed", "id": ids[0], "retmode": "xml",
                           }), xml=True)
            articles = root.findall("./PubmedArticle")
            if len(articles) != 1:
                raise LookupProblem("expected exactly one PubMed article")
            article = articles[0]
            record, dois = pubmed_record(article)
            show("PubMed", record)
            if record["PMID"] != ids[0] or dois != [doi]:
                warnings.append("PubMed DOI/PMID identity mismatch or ambiguous DOI list")
            for link in article.findall("./MedlineCitation/CommentsCorrectionsList/"
                                        "CommentsCorrections"):
                notice_count += 1
                warnings.append("PubMed related notice/link: " +
                                clean(link.get("RefType", "UNKNOWN")) +
                                " PMID=" + (text(link, "PMID") or "UNKNOWN") +
                                " | " + text(link, "RefSource"))
            if re.search(r"retract|erratum|concern|correct|withdraw",
                         record["Type"] + " " + record["Title"], re.I):
                notice_count += 1
                warnings.append("PubMed publication type/title signals a notice")
    except (LookupProblem, KeyError, TypeError, ValueError, AttributeError) as exc:
        warnings.append("PubMed UNKNOWN: " + clean(str(exc)))

    if len(records) == 2:
        for key in ("Title", "Journal", "Authors"):
            if norm(records["Crossref"][key]) != norm(records["PubMed"][key]):
                warnings.append(key + " differs between sources (formatting may differ)")
        if not set(records["Crossref"]["Year"].split("/")) & set(
                records["PubMed"]["Year"].split("/")):
            warnings.append("Publication years differ between sources")
    lines.append("\nWarnings:")
    lines.extend("- " + warning for warning in warnings)
    if not notice_count:
        lines.append("- No notice detected in returned API fields; "
                     "this does NOT establish that no retraction/correction exists.")
    lines.append("- Publisher page, DOI resolution, abstract/full text and claim fit "
                 "were NOT checked. Retraction status remains provisional. "
                 "Do not authorize a citation from this output alone.")
    lines.append("Status: " + ("REVIEW_REQUIRED" if warnings else
                              "METADATA_ONLY / manual publisher and content review required"))
    return "\n".join(lines), 1 if warnings else 0


def search_pubmed(words):
    """Return a few public candidates. Caller supplies generic medical keywords only."""
    words = " ".join(words.split())
    if not re.fullmatch(r"[A-Za-z0-9 ,()/'-]{3,180}", words):
        raise ValueError("Use brief English medical keywords only.")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    url = EUTILS + "esearch.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed", "term": words, "retmax": 6, "retmode": "json", "sort": "relevance"})
    ids = request(opener, url)["esearchresult"]["idlist"]
    if not ids:
        print("No candidates for this search.")
        return 0
    if len(ids) > 6 or not all(i.isdigit() for i in ids):
        raise LookupProblem("Unexpected PubMed candidates")
    time.sleep(0.35)
    xml = request(opener, EUTILS + "efetch.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(ids), "retmode": "xml"}), xml=True)
    for article in xml.findall("./PubmedArticle"):
        record, _ = pubmed_record(article)
        print(record["Title"], "|", record["Journal"], record["Year"],
              "| PMID:", record["PMID"], "| DOI:", record["DOI"])
    return 0


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2 and args[0] == "--search":
        try:
            return search_pubmed(args[1])
        except (LookupProblem, ValueError, KeyError, TypeError, OSError) as err:
            print("Search unresolved:", clean(err))
            return 1
    if len(args) != 1 or len(args[0]) > 512 or not DOI_RE.fullmatch(args[0]):
        print("Usage: python check_doi.py DOI\n"
              "Provide one bare DOI identifier only; URLs, whitespace, email, "
              "query strings and unsupported DOI characters are rejected.")
        return 2
    doi = args[0].casefold()
    results = queue.Queue()

    def run():
        try:
            results.put(lookup(doi))
        except Exception:
            # Malformed upstream data must not escape as apparent success.
            results.put(("Status: REVIEW_REQUIRED\n"
                         "Warnings: unexpected response/processing failure; "
                         "identity and notice status UNKNOWN.", 1))

    # The daemon bounds the whole CLI even if DNS or a slow response stalls.
    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    try:
        output, code = results.get(timeout=TOTAL_TIMEOUT)
    except queue.Empty:
        output, code = ("Status: REVIEW_REQUIRED\n"
                        "Warnings: total 45-second lookup deadline exceeded; "
                        "identity and notice status UNKNOWN.", 1)
    print(output)
    return code


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStatus: INTERRUPTED; lookup incomplete.")
        sys.exit(130)
