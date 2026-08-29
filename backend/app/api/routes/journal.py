from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_student_or_404
from app.db.models import JournalEvent, JournalRun, Student
from app.journal.runner import run_nightly_check

router = APIRouter(prefix="/students", tags=["journal"])


class JournalEventOut(BaseModel):
    kind: str
    detail: str
    worth_telling: bool


class JournalRunOut(BaseModel):
    id: int
    ran_at: datetime
    sources_checked: int
    citations_verified: int
    rules_evaluated: int
    changes_found: int
    messages_sent: int
    seconds_taken: float
    was_silent: bool
    checks_run: int
    events: list[JournalEventOut] = []


def _to_out(run: JournalRun, events: list[JournalEvent]) -> JournalRunOut:
    return JournalRunOut(
        id=run.id,
        ran_at=run.ran_at,
        sources_checked=run.sources_checked,
        citations_verified=run.citations_verified,
        rules_evaluated=run.rules_evaluated,
        changes_found=run.changes_found,
        messages_sent=run.messages_sent,
        seconds_taken=run.seconds_taken,
        was_silent=run.messages_sent == 0,
        checks_run=run.citations_verified + run.rules_evaluated,
        events=[
            JournalEventOut(kind=e.kind, detail=e.detail, worth_telling=e.worth_telling)
            for e in events
        ],
    )


def _events_for(db: Session, run_id: int) -> list[JournalEvent]:
    return list(db.scalars(select(JournalEvent).where(JournalEvent.run_id == run_id)).all())


@router.get("/{student_id}/journal", response_model=list[JournalRunOut])
def read_journal(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=60),
) -> list[JournalRunOut]:
    runs = db.scalars(
        select(JournalRun)
        .where(JournalRun.student_id == student.id)
        .order_by(JournalRun.ran_at.desc())
        .limit(limit)
    ).all()
    return [_to_out(run, _events_for(db, run.id)) for run in runs]


@router.post("/{student_id}/journal/run", response_model=JournalRunOut, status_code=201)
def trigger_run(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
    today: date | None = Query(default=None),
) -> JournalRunOut:
    run = run_nightly_check(db, student_id=student.id, today=today)
    return _to_out(run, _events_for(db, run.id))
