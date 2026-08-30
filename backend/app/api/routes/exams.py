from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import ExamRuleRecord, SourceDocument
from app.apply.links import ApplyLink, apply_links_for
from app.core.config import get_settings
from app.extraction.document import load_pages
from app.extraction.schema import ExamRules

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("")
def list_exams(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    records = db.scalars(select(ExamRuleRecord).order_by(ExamRuleRecord.exam_name)).all()
    return [
        {
            "exam_name": r.exam_name,
            "source_id": r.source_id,
            "document_sha256": r.document_sha256,
            "readable": r.is_readable,
        }
        for r in records
    ]


@router.get("/{document_sha256}")
def read_exam(document_sha256: str, db: Session = Depends(get_db)) -> dict[str, object]:
    record = db.scalar(
        select(ExamRuleRecord).where(ExamRuleRecord.document_sha256 == document_sha256)
    )
    if record is None:
        raise HTTPException(status_code=404, detail="no rules for that document")

    document = db.scalar(
        select(SourceDocument).where(SourceDocument.sha256 == document_sha256)
    )
    rules = ExamRules.model_validate(record.payload)

    return {
        "exam_name": rules.exam_name,
        "source_id": rules.source_id,
        "document": {
            "title": document.title if document else rules.exam_name,
            "origin_url": document.origin_url if document else None,
            "page_count": document.page_count if document else None,
        },
        "age": rules.age.model_dump(mode="json") if rules.age else None,
        "age_relaxations": [r.model_dump(mode="json") for r in rules.age_relaxations],
        "qualifications": [q.model_dump(mode="json") for q in rules.qualifications],
        "fees": [f.model_dump(mode="json") for f in rules.fees],
        "key_dates": [d.model_dump(mode="json") for d in rules.key_dates],
        "could_not_verify": rules.could_not_verify,
        "citation_count": len(rules.all_citations()),
    }


@router.get("/{document_sha256}/apply-links", response_model=list[ApplyLink])
def read_apply_links(document_sha256: str, db: Session = Depends(get_db)) -> list[ApplyLink]:
    document = db.scalar(
        select(SourceDocument).where(SourceDocument.sha256 == document_sha256)
    )
    if document is None:
        raise HTTPException(status_code=404, detail="no such document")

    root = get_settings().notifications_path
    pages = load_pages(root / document.relative_path)
    return apply_links_for(document.source_id, pages)
