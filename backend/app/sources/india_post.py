from __future__ import annotations

import re

from app.sources.base import Notice
from app.sources.html_notices import collect_pdf_notices

id = "india_post"
name = "India Post, Gramin Dak Sevak"
home_url = "https://indiapostgdsonline.gov.in"
official_domains = ("indiapostgdsonline.gov.in", "cept.gov.in", "indiapost.gov.in")

PAGES = [
    "https://indiapostgdsonline.gov.in/",
    "https://indiapostgdsonline.cept.gov.in/",
]

WORTH_READING = re.compile(
    r"notification|schedule|engagement|vacan|advertis|corrigend|instruction",
    re.IGNORECASE,
)

RESULT_LISTS = re.compile(
    r"shortlisted|supplimentary|supplementary|_dv_|docverlist|merit|result|annexure",
    re.IGNORECASE,
)


def _is_about_applying(notice: Notice) -> bool:
    haystack = f"{notice.title} {notice.document_url or ''}"
    if RESULT_LISTS.search(haystack):
        return False
    return bool(WORTH_READING.search(haystack))


def fetch_notices() -> list[Notice]:
    found = collect_pdf_notices(id, PAGES, official_domains, referer=home_url + "/")
    return [notice for notice in found if _is_about_applying(notice)]
