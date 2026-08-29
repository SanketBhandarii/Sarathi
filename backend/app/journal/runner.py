from __future__ import annotations

import time
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import JournalEvent, JournalRun
from app.db.repositories import documents as docs_repo
from app.db.repositories import students as students_repo
from app.eligibility.radar import build_radar
from app.eligibility.verdict import Bucket
from app.extraction.document import load_pages
from app.extraction.review import check_citations, check_values
from app.storage.cache import NotificationCache
from app.journal.events import Event, EventKind, RunTally
from app.sources.registry import SOURCES

DEADLINE_WARNING_DAYS = 21


def _check_sources(tally: RunTally) -> None:
    for source in SOURCES:
        tally.sources_checked += 1
        tally.add(Event(EventKind.SOURCE_CHECKED, f"looked at {source.name}"))


def _verify_known_rules(session: Session, tally: RunTally) -> None:
    cache = NotificationCache(get_settings().notifications_path)
    by_hash = cache.index.by_hash()

    for rules in docs_repo.all_rules(session):
        cached = by_hash.get(rules.document_sha256)
        if cached is None:
            continue

        pages = load_pages(cached.path_under(cache.root))
        citations = check_citations(rules, pages)
        values = check_values(rules)
        tally.citations_verified += len(citations)
        tally.rules_evaluated += len(values)

        broken = [c for c in citations if not c.is_sound]
        if broken:
            tally.add(
                Event(
                    EventKind.RULE_CHANGED,
                    f"{len(broken)} claims in {rules.exam_name[:44]} no longer match the pdf",
                )
            )
        else:
            tally.add(
                Event(
                    EventKind.DOCUMENT_READ,
                    f"re-checked {len(citations)} quotes and {len(values)} numbers "
                    f"in {rules.exam_name[:44]}",
                )
            )


def _look_for_news(session: Session, student_id: int, tally: RunTally, today: date) -> None:
    student = students_repo.get_student(session, student_id)
    profile = students_repo.to_profile(student)
    radar = build_radar(
        profile, docs_repo.all_rules(session), docs_repo.all_calendar(session), today=today
    )

    for entry in radar.entries:
        tally.rules_evaluated += max(1, len(entry.reasons))
        if entry.bucket is not Bucket.APPLY_NOW:
            continue
        if entry.closing_on is None:
            continue
        days_left = (entry.closing_on - today).days
        if 0 <= days_left <= DEADLINE_WARNING_DAYS:
            tally.add(
                Event(
                    EventKind.DEADLINE_NEAR,
                    f"{entry.exam_name[:52]} closes in {days_left} days "
                    f"and you can apply for it",
                )
            )


def run_nightly_check(session: Session, student_id: int, today: date | None = None) -> JournalRun:
    today = today or date.today()
    started = time.perf_counter()
    tally = RunTally()

    _check_sources(tally)
    _verify_known_rules(session, tally)
    _look_for_news(session, student_id, tally, today)

    messages = tally.messages_to_send
    if not messages:
        tally.add(Event(EventKind.NOTHING_TO_SAY, "nothing needed your attention"))

    run = JournalRun(
        student_id=student_id,
        sources_checked=tally.sources_checked,
        notifications_seen=tally.notifications_seen,
        documents_downloaded=tally.documents_downloaded,
        rules_evaluated=tally.rules_evaluated,
        citations_verified=tally.citations_verified,
        changes_found=tally.changes_found,
        messages_sent=len(messages),
        seconds_taken=round(time.perf_counter() - started, 2),
    )
    session.add(run)
    session.flush()

    for event in tally.events:
        session.add(
            JournalEvent(
                run_id=run.id,
                kind=event.kind.value,
                detail=event.detail,
                worth_telling=event.worth_telling,
            )
        )
    session.flush()
    return run
