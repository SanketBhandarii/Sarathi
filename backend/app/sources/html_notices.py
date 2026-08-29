from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.http import build_client
from app.sources.base import Notice, is_official_url


def collect_pdf_notices(
    source_id: str,
    page_urls: list[str],
    official_domains: tuple[str, ...],
    referer: str,
    min_title_length: int = 12,
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

                title = " ".join(anchor.get_text(" ", strip=True).split())
                if len(title) < min_title_length:
                    continue

                seen.add(document_url)
                notices.append(
                    Notice(
                        source_id=source_id,
                        title=title,
                        detail_url=page_url,
                        document_url=document_url,
                    )
                )
    return notices
