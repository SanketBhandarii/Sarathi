from __future__ import annotations

import sys

from app.core.config import get_settings
from app.db.base import session_scope
from app.db.repositories import documents as docs_repo
from app.db.repositories import students as students_repo
from app.extraction.store import ExamRulesStore
from app.storage.cache import NotificationCache
from app.storage.calendar_store import CalendarStore
from app.student.samples import RAVI


def main() -> int:
    settings = get_settings()
    cache = NotificationCache(settings.notifications_path)
    rules_store = ExamRulesStore(settings.exams_path)
    calendar_store = CalendarStore(settings.exams_path)

    with session_scope() as session:
        for document in cache.index.documents:
            docs_repo.upsert_document(session, document)
        for rules in rules_store.all():
            docs_repo.upsert_rules(session, rules)
        for entry in calendar_store.get():
            docs_repo.upsert_calendar(session, entry)

        if students_repo.first_student(session) is None:
            students_repo.save_profile(session, RAVI)

        session.flush()
        print(f"documents      {len(cache.index.documents)}")
        print(f"exam rules     {len(rules_store.all())}")
        print(f"calendar exams {len(calendar_store.get())}")

    with session_scope() as session:
        student = students_repo.first_student(session)
        print(f"student        {student.name} (id {student.id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
