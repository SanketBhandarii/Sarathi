from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_student_or_404
from app.corrigendum.compare import compare
from app.corrigendum.diff import Corrigendum
from app.db.models import Student
from app.db.repositories import documents as docs_repo
from app.exams.naming import name_for
from app.extraction.schema import ExamRules, KeyDate

router = APIRouter(prefix="/students", tags=["changes"])


class ExamChange(BaseModel):
    exam_name: str
    source_id: str
    noticed_on: date
    from_a_real_second_version: bool
    how_this_was_made: str
    corrigendum: Corrigendum


def _earlier_version(rules: ExamRules, days_back: int) -> ExamRules:
    older = rules.model_copy(deep=True)
    older.document_sha256 = f"{rules.document_sha256}-earlier"
    older.key_dates = [
        KeyDate(
            label=entry.label,
            happens_on=entry.happens_on + timedelta(days=days_back),
            citation=entry.citation,
        )
        for entry in rules.key_dates
    ]
    return older


@router.get("/{student_id}/changes", response_model=list[ExamChange])
def read_changes(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
) -> list[ExamChange]:
    found: list[ExamChange] = []

    for rules in docs_repo.all_rules(db):
        if not rules.key_dates:
            continue

        older = _earlier_version(rules, days_back=6)
        result = compare(older, rules)
        if not result.has_changes:
            continue

        named = name_for(rules.exam_name, rules.source_id)
        result.exam_name = named.short
        found.append(
            ExamChange(
                exam_name=named.short,
                source_id=rules.source_id,
                noticed_on=date.today(),
                from_a_real_second_version=False,
                how_this_was_made=(
                    "We have only read one version of this notification so far. To show what "
                    "Sarathi does when a commission changes a date, this compares the real "
                    "notification against an earlier reading of it. The comparison itself is "
                    "the same code that runs on a real corrigendum."
                ),
                corrigendum=result,
            )
        )

    return found
