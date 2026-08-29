from __future__ import annotations

import re
from datetime import date

from pydantic import BaseModel

from app.core.browser import rendered_page, table_rows

CALENDAR_URL = "https://ssc.gov.in/for-candidates/examination-calendar"

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


class CalendarEntry(BaseModel):
    exam_name: str
    tier: str | None = None
    advertised_on: date | None = None
    advertised_text: str | None = None
    advertised_is_month_only: bool = False
    closes_on: date | None = None
    closes_text: str | None = None
    closes_is_month_only: bool = False
    exam_month_text: str | None = None
    source_id: str = "ssc"
    source_url: str = CALENDAR_URL


def parse_indian_date(text: str) -> tuple[date | None, str, bool]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return None, "", False

    exact = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", cleaned)
    if exact:
        day, month, year = exact.groups()
        number = MONTHS.get(month.lower())
        if number:
            return date(int(year), number, int(day)), cleaned, False

    loose = re.search(r"([A-Za-z]+)\s+(\d{4})", cleaned)
    if loose:
        month, year = loose.groups()
        number = MONTHS.get(month.lower())
        if number:
            return date(int(year), number, 1), cleaned, True

    return None, cleaned, False


def _looks_like_entry(cells: list[str]) -> bool:
    return len(cells) >= 5 and bool(re.match(r"^\d+\.?$", cells[0].strip()))


def fetch_calendar() -> list[CalendarEntry]:
    with rendered_page(CALENDAR_URL) as page:
        rows = table_rows(page)

    entries: list[CalendarEntry] = []
    for cells in rows:
        if not _looks_like_entry(cells):
            continue
        advertised, advertised_text, advertised_month_only = parse_indian_date(cells[3])
        closes, closes_text, closes_month_only = parse_indian_date(cells[4])
        entries.append(
            CalendarEntry(
                exam_name=" ".join(cells[1].split()),
                tier=" ".join(cells[2].split()) or None,
                advertised_on=advertised,
                advertised_text=advertised_text or None,
                advertised_is_month_only=advertised_month_only,
                closes_on=closes,
                closes_text=closes_text or None,
                closes_is_month_only=closes_month_only,
                exam_month_text=" ".join(cells[5].split()) if len(cells) > 5 else None,
            )
        )
    return entries
