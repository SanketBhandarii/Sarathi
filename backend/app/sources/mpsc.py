from __future__ import annotations

import re
from datetime import date

from pydantic import BaseModel
from playwright.sync_api import sync_playwright

from app.core.http import BROWSER_USER_AGENT

id = "mpsc"
name = "Maharashtra Public Service Commission"
home_url = "https://mpsc.gov.in"
official_domains = ("mpsc.gov.in",)
state = "Maharashtra"
NOTIFICATIONS_URL = "https://mpsc.gov.in/adv_notification/8"


class MpscDocument(BaseModel):
    advt_no: str
    subject: str
    published_on: date | None
    payload_size: int
    source_id: str = id


def _parse_date(text: str) -> date | None:
    match = re.search(r"(\d{2})-(\d{2})-(\d{4})", text.strip())
    if not match:
        return None
    day, month, year = (int(g) for g in match.groups())
    return date(year, month, day)


def fetch_documents(limit: int = 6) -> list[tuple[MpscDocument, bytes]]:
    collected: list[tuple[MpscDocument, bytes]] = []

    with sync_playwright() as driver:
        browser = driver.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                accept_downloads=True, user_agent=BROWSER_USER_AGENT
            )
            page = context.new_page()
            page.goto(NOTIFICATIONS_URL, wait_until="networkidle", timeout=70000)
            page.wait_for_timeout(6000)

            for row in page.query_selector_all("table tr")[1 : limit + 1]:
                cells = row.query_selector_all("td")
                if len(cells) < 5:
                    continue
                link = cells[-1].query_selector("a")
                if link is None:
                    continue
                try:
                    with page.expect_download(timeout=60000) as download_info:
                        link.click()
                    payload = download_info.value.path().read_bytes()
                except Exception:
                    continue

                collected.append(
                    (
                        MpscDocument(
                            advt_no=" ".join(cells[1].inner_text().split()),
                            subject=" ".join(cells[2].inner_text().split()),
                            published_on=_parse_date(cells[3].inner_text()),
                            payload_size=len(payload),
                        ),
                        payload,
                    )
                )
        finally:
            browser.close()
    return collected
