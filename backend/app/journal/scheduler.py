from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.db.base import session_scope
from app.db.models import JournalRun, Student
from app.journal.runner import run_nightly_check
from app.language.phrases import Language

log = logging.getLogger("sarathi.scheduler")

IST = timezone(timedelta(hours=5, minutes=30))
RUN_AT = time(hour=2, minute=15)


def next_run_after(now: datetime) -> datetime:
    here = now.astimezone(IST)
    today_run = datetime.combine(here.date(), RUN_AT, tzinfo=IST)
    return today_run if here < today_run else today_run + timedelta(days=1)


def already_ran_today(student_id: int, today: date) -> bool:
    with session_scope() as session:
        latest = session.scalar(
            select(JournalRun)
            .where(JournalRun.student_id == student_id)
            .order_by(JournalRun.ran_at.desc())
            .limit(1)
        )
        if latest is None or latest.ran_at is None:
            return False
        stamp = latest.ran_at
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.astimezone(IST).date() >= today


def run_for_everyone(today: date | None = None) -> int:
    when = today or datetime.now(IST).date()
    done = 0

    with session_scope() as session:
        students = [(s.id, s.language) for s in session.scalars(select(Student)).all()]

    for student_id, language in students:
        if already_ran_today(student_id, when):
            continue
        try:
            with session_scope() as session:
                run_nightly_check(
                    session,
                    student_id=student_id,
                    today=when,
                    language=Language(language),
                )
            done += 1
        except Exception:
            log.exception("nightly check failed for student %s", student_id)

    log.info("nightly check ran for %s student(s)", done)
    return done


async def watch_the_clock() -> None:
    while True:
        now = datetime.now(timezone.utc)
        wake_at = next_run_after(now)
        seconds = max(30.0, (wake_at - now.astimezone(IST)).total_seconds())
        log.info("next nightly check at %s (in %.0f minutes)", wake_at, seconds / 60)

        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            log.info("scheduler stopped")
            raise

        try:
            await asyncio.to_thread(run_for_everyone)
        except Exception:
            log.exception("nightly check failed")


def is_enabled() -> bool:
    return get_settings().run_nightly_checks
