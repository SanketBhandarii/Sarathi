from __future__ import annotations

import re
from urllib.parse import unquote, urljoin

from bs4 import BeautifulSoup

from app.core.http import build_client
from app.sources.base import Notice, is_official_url

JUNK_TITLE = re.compile(r"^[\s(\[]*(\d+(\.\d+)?\s*(kb|mb|bytes?)|pdf|download|click here|view)[\s)\]]*$", re.I)


SIZE_SUFFIX = re.compile(r"\s*[\(\[]\s*\d+(\.\d+)?\s*(kb|mb|bytes?)\s*[\)\]]\s*$", re.I)


def _clean(text: str) -> str:
    collapsed = " ".join(text.split())
    return SIZE_SUFFIX.sub("", collapsed).strip()


def _title_from_filename(url: str) -> str:
    name = unquote(url.rsplit("/", 1)[-1])
    name = re.sub(r"\.pdf$", "", name, flags=re.I)
    return _clean(re.sub(r"[_\-]+", " ", name))


def _best_title(anchor, document_url: str) -> str:
    candidates = [_clean(anchor.get_text(" ", strip=True))]

    parent = anchor.find_parent(["li", "td", "tr", "p", "div"])
    if parent is not None:
        candidates.append(_clean(parent.get_text(" ", strip=True)))

    for value in candidates:
        if value and not JUNK_TITLE.match(value) and len(value) >= 10:
            return value[:220]
    return _title_from_filename(document_url)[:220]


def collect_pdf_notices(
    source_id: str,
    page_urls: list[str],
    official_domains: tuple[str, ...],
    referer: str,
) -> list[Notice]:
    seen: set[str] = set()
    notices: list[Notice] = []

    with build_client(referer=referer) as client:
        for page_url in page_urls:
            try:
                response = client.get(page_url)
                response.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(response.text, "lxml")
            for anchor in soup.find_all("a", href=True):
                document_url = urljoin(str(response.url), anchor["href"])
                if ".pdf" not in document_url.lower():
                    continue
                if not is_official_url(document_url, official_domains):
                    continue
                if document_url in seen:
                    continue

                seen.add(document_url)
                notices.append(
                    Notice(
                        source_id=source_id,
                        title=_best_title(anchor, document_url),
                        detail_url=page_url,
                        document_url=document_url,
                    )
                )
    return notices
