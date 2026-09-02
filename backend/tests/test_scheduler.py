from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import delete, select

from app.db.base import session_scope
from app.db.models import JournalEvent, JournalRun
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


def test_before_it_runs_today_is_not_done(one_night):
    assert one_night.was_done_before is False


def test_a_run_actually_happens_and_is_written_down(one_night):
    assert one_night.students_done >= 1
    assert _runs_for(one_night.student_id) == 1


def test_it_knows_today_is_done_once_it_has_run(one_night):
    assert already_ran_today(one_night.student_id, _today()) is True


def test_it_does_not_run_twice_on_the_same_day(one_night):
    run_for_everyone(today=_today())
    assert _runs_for(one_night.student_id) == 1


class OneNight:
    def __init__(self, student_id: int, was_done_before: bool, students_done: int) -> None:
        self.student_id = student_id
        self.was_done_before = was_done_before
        self.students_done = students_done


@pytest.fixture(scope="module")
def one_night(student_id):
    _forget_runs(student_id)
    was_done_before = already_ran_today(student_id, _today())
    students_done = run_for_everyone(today=_today())

    yield OneNight(student_id, was_done_before, students_done)

    _forget_runs(student_id)


def _today() -> date:
    return datetime.now(IST).date()


def _runs_for(student_id: int) -> int:
    with session_scope() as session:
        return len(
            session.scalars(select(JournalRun).where(JournalRun.student_id == student_id)).all()
        )


def _forget_runs(student_id: int) -> None:
    with session_scope() as session:
        ids = session.scalars(
            select(JournalRun.id).where(JournalRun.student_id == student_id)
        ).all()
        if ids:
            session.execute(delete(JournalEvent).where(JournalEvent.run_id.in_(ids)))
            session.execute(delete(JournalRun).where(JournalRun.id.in_(ids)))
