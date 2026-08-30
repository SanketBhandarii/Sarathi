from __future__ import annotations

import sys

from sqlalchemy import delete, func, select

from app.db.base import session_scope
from app.db.models import (
    Deadline,
    EmailCode,
    JournalEvent,
    JournalRun,
    QualificationRecord,
    Student,
    User,
)

ORDER = [
    (JournalEvent, "journal events"),
    (JournalRun, "journal runs"),
    (Deadline, "deadlines"),
    (QualificationRecord, "qualifications"),
    (EmailCode, "email codes"),
    (User, "users"),
    (Student, "students"),
]


def main() -> int:
    with session_scope() as session:
        for model, label in ORDER:
            before = session.scalar(select(func.count()).select_from(model)) or 0
            session.execute(delete(model))
            print(f"  removed {before:>4}  {label}")

    with session_scope() as session:
        print()
        for model, label in ORDER:
            left = session.scalar(select(func.count()).select_from(model)) or 0
            print(f"  {label:<18} {left} left")

    print()
    print("exam data was left alone. sign up again to make a fresh account.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
