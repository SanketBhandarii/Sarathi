from __future__ import annotations

import sys
from datetime import date

from sqlalchemy import select

from app.db.base import session_scope
from app.db.models import Student
from app.journal.runner import run_nightly_check
from app.language.phrases import Language


def main(day: str | None = None, send_to: str | None = None) -> int:
    today = date.fromisoformat(day) if day else date.today()
    sent_total = 0

    with session_scope() as session:
        students = session.scalars(select(Student)).all()
        for student in students:
            language = Language(student.language)
            run = run_nightly_check(
                session,
                student_id=student.id,
                today=today,
                send_to=send_to,
                language=language,
            )
            sent_total += run.messages_sent
            state = "silent" if run.messages_sent == 0 else f"{run.messages_sent} sent"
            print(
                f"  {student.name:<20} {run.citations_verified + run.rules_evaluated:>4} checks, {state}"
            )

    print()
    print(f"ran for {len(students)} student(s) on {today}, {sent_total} message(s) sent")
    return 0


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else None
    to = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(main(day, to))
