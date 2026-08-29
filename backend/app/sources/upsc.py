from __future__ import annotations

from app.sources.base import Notice
from app.sources.html_notices import collect_pdf_notices

id = "upsc"
name = "Union Public Service Commission"
home_url = "https://www.upsc.gov.in"
official_domains = ("upsc.gov.in", "upsconline.nic.in")

PAGES = [
    "https://www.upsc.gov.in",
    "https://www.upsc.gov.in/recruitment/recruitment-advertisement",
    "https://www.upsc.gov.in/examinations/active-examinations",
]


def fetch_notices() -> list[Notice]:
    return collect_pdf_notices(id, PAGES, official_domains, referer=home_url + "/")
