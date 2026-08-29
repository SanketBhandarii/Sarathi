from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import Page, sync_playwright

from app.core.http import BROWSER_USER_AGENT


@contextmanager
def rendered_page(url: str, settle_ms: int = 3500, timeout_ms: int = 60000) -> Iterator[Page]:
    with sync_playwright() as driver:
        browser = driver.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent=BROWSER_USER_AGENT)
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            page.wait_for_timeout(settle_ms)
            yield page
        finally:
            browser.close()


def table_rows(page: Page, selector: str = "table tr") -> list[list[str]]:
    return page.eval_on_selector_all(
        selector,
        "els => els.map(tr => [...tr.querySelectorAll('th,td')].map(c => c.innerText.trim()))",
    )
