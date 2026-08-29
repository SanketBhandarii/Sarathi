from __future__ import annotations

import sys
from datetime import date

from app.core.config import get_settings
from app.eligibility.engine import decide
from app.extraction.store import ExamRulesStore
from app.student.samples import RAVI


def main() -> int:
    today = date(2026, 8, 29)
    store = ExamRulesStore(get_settings().exams_path)

    student = RAVI
    print(f"{student.name}, {student.category.value}, {student.district}, {student.state}")
    print(f"born {student.date_of_birth.strftime('%d %B %Y')}, "
          f"{student.education.degree} {student.education.stream} {student.education.percentage:g}%")
    print("=" * 74)

    for rules in store.all():
        verdict = decide(rules, student, today=today)
        print()
        print(f"{verdict.exam_name}  [{verdict.source_id}]")
        print(f"  >> {verdict.headline}")
        for reason in verdict.reasons:
            mark = "!" if reason.blocks_application else "-"
            print(f"   {mark} {reason.text}")
            if reason.citation:
                print(f'       page {reason.citation.page}: "{reason.citation.quote[:88]}"')
        if verdict.unchecked:
            print(f"   ? could not check: {', '.join(verdict.unchecked[:3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
