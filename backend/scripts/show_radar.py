from __future__ import annotations

import sys
from datetime import date

from app.core.config import get_settings
from app.eligibility.layers import LAYER_LABEL, Layer
from app.eligibility.radar import build_radar
from app.eligibility.verdict import Bucket
from app.extraction.store import ExamRulesStore
from app.storage.calendar_store import CalendarStore
from app.student.samples import RAVI

MARK = {
    Bucket.APPLY_NOW: "[apply now]",
    Bucket.COMING_SOON: "[coming soon]",
    Bucket.NOT_YET: "[not yet]",
    Bucket.CLOSED_FOR_NOW: "[closed, runs again]",
    Bucket.NOT_FOR_YOU: "[not for you]",
    Bucket.UNKNOWN: "[could not check]",
}


def main() -> int:
    settings = get_settings()
    today = date(2026, 8, 29)
    student = RAVI
    radar = build_radar(
        student,
        ExamRulesStore(settings.exams_path).all(),
        CalendarStore(settings.exams_path).get(),
        today=today,
    )

    print(f"Sarathi   {student.name}, {student.category.value}, {student.district}, {student.state}")
    print(f"{today.strftime('%d %B %Y')}   {len(radar.entries)} exams watched")

    for layer in Layer:
        rows = radar.layer(layer)
        if not rows:
            continue
        print()
        print("=" * 78)
        print(f"{LAYER_LABEL[layer].upper()}   ({len(rows)})")
        for entry in rows:
            closing = f"   closes {entry.closing_text}" if entry.closing_text else ""
            print(f"  {MARK[entry.bucket]:<22} {entry.exam_name[:44]:<46}{closing}")
            if entry.bucket is Bucket.APPLY_NOW and entry.rules_known:
                for reason in entry.reasons[:2]:
                    print(f"      {reason.text[:82]}")
            if entry.unchecked:
                print(f"      not checked: {entry.unchecked[0][:66]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
