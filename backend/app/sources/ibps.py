from __future__ import annotations

from app.sources.base import Notice
from app.sources.html_notices import collect_pdf_notices

id = "ibps"
name = "Institute of Banking Personnel Selection"
home_url = "https://www.ibps.in"
official_domains = ("ibps.in",)

PAGES = [
    "https://www.ibps.in",
    "https://www.ibps.in/index.php/crp-po-mt/",
    "https://www.ibps.in/index.php/crp-clerical/",
]


def fetch_notices() -> list[Notice]:
    return collect_pdf_notices(id, PAGES, official_domains, referer=home_url + "/")
