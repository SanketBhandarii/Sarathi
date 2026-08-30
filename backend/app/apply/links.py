from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from pydantic import BaseModel, computed_field

from app.core.http import build_client
from app.extraction.document import Page

OFFICIAL_SUFFIXES = (".gov.in", ".nic.in")

KNOWN_PORTALS: dict[str, tuple[str, str]] = {
    "ssc": ("https://ssc.gov.in/candidate-portal", "Staff Selection Commission candidate portal"),
    "upsc": ("https://upsconline.gov.in/", "UPSC online application portal"),
    "ibps": ("https://www.ibps.in/", "IBPS official website"),
    "mpsc": ("https://mpsconline.gov.in/", "MPSC online application portal"),
}

EXTRA_OFFICIAL_HOSTS = {
    "ibps.in",
    "www.ibps.in",
    "ibpsreg.ibps.in",
    "upsconline.nic.in",
    "upsconline.gov.in",
}

URL_PATTERN = re.compile(r"https?://[a-zA-Z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", re.IGNORECASE)
TRAILING_JUNK = re.compile(r"[).,;:'\"\]]+$")


class ApplyLink(BaseModel):
    url: str
    label: str
    source_id: str
    is_official: bool
    reachable: bool | None = None
    http_status: int | None = None
    checked_at: datetime | None = None

    @computed_field
    @property
    def host(self) -> str:
        return urlparse(self.url).hostname or ""

    @computed_field
    @property
    def can_show(self) -> bool:
        return self.is_official and self.reachable is not False

    @computed_field
    @property
    def note(self) -> str:
        if not self.is_official:
            return "This link does not belong to the commission, so we do not show it."
        if self.reachable is False:
            return "The commission's page is not opening right now. Try again later."
        if self.reachable is None:
            return "We have not checked this link yet."
        return "This goes straight to the commission's own page. No advertisements."


def is_official_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    if host in EXTRA_OFFICIAL_HOSTS:
        return True
    return any(host.endswith(suffix) for suffix in OFFICIAL_SUFFIXES)


def urls_in_pages(pages: list[Page], limit: int = 40) -> list[str]:
    seen: list[str] = []
    for page in pages:
        for match in URL_PATTERN.findall(page.text):
            url = TRAILING_JUNK.sub("", match)
            if url not in seen:
                seen.append(url)
            if len(seen) >= limit:
                return seen
    return seen


def official_urls_in_pages(pages: list[Page]) -> list[str]:
    return [url for url in urls_in_pages(pages) if is_official_host(url)]


def check_link(url: str, referer: str) -> tuple[bool, int | None]:
    try:
        with build_client(referer=referer) as client:
            response = client.get(url)
        return response.status_code < 400, response.status_code
    except Exception:
        return False, None


def apply_links_for(
    source_id: str, pages: list[Page], verify: bool = True
) -> list[ApplyLink]:
    found: list[ApplyLink] = []

    portal = KNOWN_PORTALS.get(source_id)
    if portal:
        url, label = portal
        found.append(
            ApplyLink(url=url, label=label, source_id=source_id, is_official=is_official_host(url))
        )

    for url in official_urls_in_pages(pages):
        if any(existing.url.rstrip("/") == url.rstrip("/") for existing in found):
            continue
        found.append(
            ApplyLink(
                url=url,
                label="Link printed in the notification",
                source_id=source_id,
                is_official=True,
            )
        )

    if verify:
        for link in found:
            reachable, status = check_link(link.url, referer=link.url)
            link.reachable = reachable
            link.http_status = status
            link.checked_at = datetime.now(timezone.utc)

    return [link for link in found if link.is_official]
