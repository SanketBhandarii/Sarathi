from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select

from app.db.base import session_scope
from app.db.models import JournalRun
from app.journal.scheduler import IST, already_ran_today, next_run_after, run_for_everyone


def test_it_waits_until_tonight_if_the_time_has_not_come():
    now = datetime(2026, 8, 31, 0, 30, tzinfo=IST)
    assert next_run_after(now) == datetime(2026, 8, 31, 2, 15, tzinfo=IST)


def test_it_waits_until_tomorrow_once_today_has_run():
    now = datetime(2026, 8, 31, 10, 0, tzinfo=IST)
    assert next_run_after(now) == datetime(2026, 9, 1, 2, 15, tzinfo=IST)


def test_the_gap_is_never_more_than_a_day():
    for hour in range(24):
        now = datetime(2026, 8, 31, hour, 0, tzinfo=IST)
        assert timedelta(0) < next_run_after(now) - now <= timedelta(days=1)


def test_a_run_actually_happens_and_is_written_down(student_id):
    before = _runs_for(student_id)
    done = run_for_everyone(today=date(2026, 8, 29))
    assert done >= 1
    assert _runs_for(student_id) > before


def test_it_does_not_run_twice_on_the_same_day(student_id):
    run_for_everyone(today=date(2026, 8, 29))
    after_first = _runs_for(student_id)

    run_for_everyone(today=date(2026, 8, 29))
    assert _runs_for(student_id) == after_first


def test_it_knows_whether_today_is_done(student_id):
    run_for_everyone(today=date(2026, 8, 29))
    assert already_ran_today(student_id, datetime.now(IST).date()) is True


def _runs_for(student_id: int) -> int:
    with session_scope() as session:
        return len(
            session.scalars(
                select(JournalRun).where(JournalRun.student_id == student_id)
            ).all()
        )
