from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class Page:
    number: int
    text: str


@dataclass(frozen=True)
class Snippet:
    page: int
    text: str


AGE_PATTERNS = (r"\bage\b", r"relaxation", r"born not earlier", r"upper age")
QUALIFICATION_PATTERNS = (r"qualification", r"educational", r"degree", r"graduat")
FEE_PATTERNS = (r"application fee", r"intimation charge", r"\bfees\b")
DATE_PATTERNS = (r"important dates", r"schedule of events", r"last date", r"commencement of")
PHOTO_PATTERNS = (r"photograph image", r"photograph must be", r"passport style", r"photo capture")
SIGNATURE_PATTERNS = (r"signature\s*:", r"sign on white paper", r"not in capital letters")
THUMB_PATTERNS = (r"thumb impression", r"left thumb")
DOCUMENT_SPEC_PATTERNS = (
    r"photograph",
    r"signature",
    r"thumb impression",
    r"dimensions?\s*[:\-]?\s*\d+\s*[x×]",
    r"\d+\s*kb",
)


MIN_CHARS_PER_PAGE = 350
MIN_TOTAL_CHARS = 800


def has_readable_text(pages: list[Page]) -> bool:
    if not pages:
        return False
    total = sum(len(p.text) for p in pages)
    return total >= MIN_TOTAL_CHARS and total / len(pages) >= MIN_CHARS_PER_PAGE


def load_pages(pdf_path: Path) -> list[Page]:
    reader = PdfReader(pdf_path)
    return [
        Page(number=n, text=" ".join((p.extract_text() or "").split()))
        for n, p in enumerate(reader.pages, start=1)
    ]


def _merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def snippets_for(
    pages: list[Page],
    patterns: tuple[str, ...],
    window: int = 900,
    max_snippets: int = 3,
) -> list[Snippet]:
    found: list[tuple[int, Snippet]] = []
    for page in pages:
        spans = [
            (max(0, m.start() - window), min(len(page.text), m.end() + window))
            for pattern in patterns
            for m in re.finditer(pattern, page.text, re.IGNORECASE)
        ]
        if not spans:
            continue
        hits = len(spans)
        for start, end in _merge(spans):
            found.append((hits, Snippet(page=page.number, text=page.text[start:end])))

    ranked = sorted(found, key=lambda item: -item[0])[:max_snippets]
    return sorted((s for _, s in ranked), key=lambda s: s.page)


def render(snippets: list[Snippet], char_budget: int = 5200) -> str:
    blocks: list[str] = []
    used = 0
    for snippet in snippets:
        remaining = char_budget - used
        if remaining <= 200:
            break
        text = snippet.text[:remaining]
        opening = '<page number="' + str(snippet.page) + '">'
        blocks.append(opening + chr(10) + text + chr(10) + '</page>')
        used += len(text)
    return (chr(10) * 2).join(blocks)
