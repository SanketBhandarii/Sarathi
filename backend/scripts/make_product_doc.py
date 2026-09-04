from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from scripts.product_doc_content import PAGE_HTML

OUT = Path(__file__).resolve().parents[2] / "docs" / "sarathi-product-guide.pdf"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as engine:
        browser = engine.chromium.launch()
        page = browser.new_page()
        page.set_content(PAGE_HTML, wait_until="networkidle")
        page.wait_for_timeout(500)
        page.pdf(
            path=str(OUT),
            format="A4",
            print_background=True,
            margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
        )
        browser.close()

    print(f"written {OUT}  ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
