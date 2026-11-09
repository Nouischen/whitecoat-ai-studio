"""Optional browser fallback: open a DOI and read a small excerpt from known public journal hosts.
Other publishers are reported for the AI to open with its normal browser.
Uses Python 3.9+ standard library. No input files or credentials.
"""
import re
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOSTS = ("doi.org", "plos.org", "nature.com", "springer.com", "biomedcentral.com",
         "bmj.com", "jamanetwork.com", "thelancet.com", "europepmc.org", "ncbi.nlm.nih.gov",
         "sciencedirect.com", "wiley.com", "mdpi.com", "frontiersin.org")


def allowed(url):
    parts = urlsplit(url)
    host = parts.hostname or ""
    return (parts.scheme == "https" and not parts.username and not parts.password and
            parts.port in (None, 443) and any(host == h or host.endswith("." + h) for h in HOSTS))


class PublicRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urljoin(req.full_url, newurl)
        if not allowed(url):
            raise ValueError("請用瀏覽器打開 DOI 並核對期刊原頁，本工具不跟隨該站。")
        return super().redirect_request(req, fp, code, msg, headers, url)


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden = True
        elif tag in ("h1", "h2", "h3", "p", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = False

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip() + " ")


def open_doi(doi):
    if len(doi) > 255 or not re.fullmatch(r"10\.\d{4,9}/[^\s?#]+", doi, re.I):
        raise ValueError("請給一個 DOI 識別碼。")
    url = "https://doi.org/" + quote(doi, safe="/:;()._-")
    req = Request(url, headers={"User-Agent": "WhitecoatLiteratureReader/1.0", "Accept": "text/html"})
    with build_opener(PublicRedirects()).open(req, timeout=12) as resp:
        if resp.headers.get_content_type() != "text/html" or urlsplit(resp.geturl()).hostname == "doi.org":
            raise ValueError("本次未取得期刊 HTML 頁面，請用瀏覽器核對。")
        reader = Reader()
        reader.feed(resp.read(1800000).decode(resp.headers.get_content_charset() or "utf-8", errors="replace"))
        print("DOI", url, "\n期刊頁", resp.geturl(), "\n下列是網頁摘錄，請核對篇名、DOI、撤稿資訊及結果。")
    full = "".join(reader.parts)
    print(re.sub(r"[ \t]+", " ", full)[:48000])


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    try:
        if len(sys.argv) != 2:
            raise ValueError("用法：python open_doi.py DOI")
        open_doi(sys.argv[1])
    except (ValueError, OSError, HTTPError, URLError) as exc:
        sys.exit(str(exc))
