from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import CalendarExam, ExamRuleRecord, SourceDocument, Student

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, object]:
    def count(model) -> int:
        return db.scalar(select(func.count()).select_from(model)) or 0

    return {
        "status": "ok",
        "students": count(Student),
        "documents": count(SourceDocument),
        "exam_rules": count(ExamRuleRecord),
        "calendar_exams": count(CalendarExam),
    }
