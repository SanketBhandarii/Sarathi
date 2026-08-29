from __future__ import annotations

import sys
from datetime import date

from sqlalchemy import select

from app.db.base import session_scope
from app.db.models import JournalEvent, JournalRun
from app.journal.runner import run_nightly_check


def main(day: str | None) -> int:
    today = date.fromisoformat(day) if day else date.today()

    with session_scope() as session:
        run = run_nightly_check(session, student_id=1, today=today)
        run_id = run.id

    with session_scope() as session:
        run = session.get(JournalRun, run_id)
        events = session.scalars(
            select(JournalEvent).where(JournalEvent.run_id == run_id)
        ).all()

        print(f"Sarathi ran on {today.strftime('%d %B %Y')} and took {run.seconds_taken}s")
        print()
        print(f"  sources checked      {run.sources_checked}")
        print(f"  quotes verified      {run.citations_verified}")
        print(f"  rules evaluated      {run.rules_evaluated}")
        print(f"  things worth telling {run.changes_found}")
        print(f"  messages sent to you {run.messages_sent}")
        print()
        for event in events:
            mark = "!" if event.worth_telling else " "
            print(f"  {mark} {event.detail[:88]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
