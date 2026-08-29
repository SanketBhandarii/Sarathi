from __future__ import annotations

import sys
from datetime import date

from app.core.config import get_settings
from app.eligibility.radar import build_radar
from app.eligibility.verdict import Bucket
from app.extraction.store import ExamRulesStore
from app.storage.calendar_store import CalendarStore
from app.student.samples import RAVI

HEADINGS = {
    Bucket.APPLY_NOW: "APPLY NOW",
    Bucket.COMING_SOON: "COMING SOON",
    Bucket.NOT_YET: "NOT YET",
    Bucket.CLOSED_FOR_NOW: "CLOSED FOR NOW - RUNS AGAIN",
    Bucket.UNKNOWN: "COULD NOT CHECK",
    Bucket.NOT_FOR_YOU: "NOT FOR YOU",
}


def main() -> int:
    settings = get_settings()
    today = date(2026, 8, 29)
    radar = build_radar(
        RAVI,
        ExamRulesStore(settings.exams_path).all(),
        CalendarStore(settings.exams_path).get(),
        today=today,
    )

    student = RAVI
    print(f"Sarathi  -  {student.name}, {student.category.value}, {student.district}")
    print(f"{today.strftime('%d %B %Y')}   -   {len(radar.entries)} exams watched")
    print("=" * 76)

    for bucket, heading in HEADINGS.items():
        rows = radar.bucket(bucket)
        if not rows:
            continue
        print()
        print(f"{heading}  ({len(rows)})")
        for entry in rows:
            closing = f"  closes {entry.closing_text}" if entry.closing_text else ""
            print(f"   {entry.exam_name[:56]:<58}{closing}")
            if entry.rules_known:
                for reason in entry.reasons[:2]:
                    print(f"       {reason.text[:88]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
