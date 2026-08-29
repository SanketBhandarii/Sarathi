from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from strands import tool

from app.core.config import get_settings
from app.extraction.document import Page, load_pages
from app.extraction.review import _best_ratio, _normalise


@lru_cache(maxsize=32)
def _pages_for(sha256: str) -> tuple[Page, ...]:
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    entry = next(d for d in index["documents"] if d["sha256"] == sha256)
    return tuple(load_pages(settings.notifications_path / entry["relative_path"]))


@tool
def quote_appears_on_page(document_sha256: str, page: int, quote: str) -> str:
    """Check whether a quoted sentence really appears on a given page of a notification pdf.

    Use this before accepting any claim. It compares the quote against the actual
    text of that page and reports how closely it matches.
    """
    pages = {p.number: p for p in _pages_for(document_sha256)}
    if page not in pages:
        return f"page {page} does not exist in this document"

    ratio = _best_ratio(_normalise(quote), _normalise(pages[page].text))
    if ratio >= 0.98:
        return f"found on page {page}, exact match"
    if ratio >= 0.85:
        return f"found on page {page}, close match ({ratio:.0%}), wording differs slightly"
    return f"NOT FOUND on page {page}, best match only {ratio:.0%}"


@tool
def read_page(document_sha256: str, page: int) -> str:
    """Read the full text of one page of a notification pdf."""
    pages = {p.number: p for p in _pages_for(document_sha256)}
    if page not in pages:
        return f"page {page} does not exist in this document"
    return pages[page].text[:4000]


@tool
def find_text_in_document(document_sha256: str, phrase: str) -> str:
    """Find which pages of a notification pdf contain a phrase."""
    hits = [
        f"page {p.number}"
        for p in _pages_for(document_sha256)
        if _normalise(phrase) in _normalise(p.text)
    ]
    return ", ".join(hits) if hits else f'"{phrase}" was not found anywhere in this document'
