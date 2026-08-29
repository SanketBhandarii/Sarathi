from typing import Final

import httpx
import truststore

truststore.inject_into_ssl()

BROWSER_USER_AGENT: Final = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT: Final = httpx.Timeout(45.0, connect=20.0)


def build_client(referer: str | None = None) -> httpx.Client:
    headers = {
        "User-Agent": BROWSER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
    }
    if referer:
        headers["Referer"] = referer
    return httpx.Client(headers=headers, timeout=DEFAULT_TIMEOUT, follow_redirects=True)
