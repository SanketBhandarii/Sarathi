from __future__ import annotations

import re
from datetime import date

from app.extraction.schema import Citation, KeyDate

DAY_MONTH_YEAR = r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})"

RANGE = re.compile(
    rf"(?:from|between)\s+{DAY_MONTH_YEAR}\s+(?:to|and|till|upto|up\s*to)\s+{DAY_MONTH_YEAR}",
    re.IGNORECASE,
)

PLAIN_LAST_DATE = re.compile(
    rf"last\s+date[^.\n]{{0,80}}?{DAY_MONTH_YEAR}",
    re.IGNORECASE,
)

ABOUT_APPLYING = re.compile(
    r"appl(?:y|ication|icants)|registration|register|online\s+payment|intimation\s+charges",
    re.IGNORECASE,
)

SENTENCE_EDGE = re.compile(r"[.\n]")


def _as_date(day: str, month: str, year: str) -> date | None:
    try:
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def _sentence_around(text: str, start: int, end: int) -> str:
    left = text.rfind(".", 0, start)
    right = text.find(".", end)
    piece = text[left + 1 if left != -1 else 0 : right if right != -1 else len(text)]
    return " ".join(piece.split())


def _candidates_on(text: str, page_number: int) -> list[tuple[date, Citation]]:
    found: list[tuple[date, Citation]] = []

    for match in RANGE.finditer(text):
        sentence = _sentence_around(text, match.start(), match.end())
        if not ABOUT_APPLYING.search(sentence):
            continue
        closes = _as_date(*match.groups()[3:6])
        if closes is not None:
            found.append((closes, Citation(page=page_number, quote=sentence[:300])))

    for match in PLAIN_LAST_DATE.finditer(text):
        sentence = _sentence_around(text, match.start(), match.end())
        if not ABOUT_APPLYING.search(sentence):
            continue
        closes = _as_date(*match.groups())
        if closes is not None:
            found.append((closes, Citation(page=page_number, quote=sentence[:300])))

    return found


def find_last_date_to_apply(pages: list[str]) -> KeyDate | None:
    everything: list[tuple[date, Citation]] = []
    for number, text in enumerate(pages, start=1):
        everything.extend(_candidates_on(text, number))

    if not everything:
        return None

    closes, citation = min(everything, key=lambda item: item[0])
    return KeyDate(
        label="Last date for submission of applications",
        happens_on=closes,
        citation=citation,
    )
