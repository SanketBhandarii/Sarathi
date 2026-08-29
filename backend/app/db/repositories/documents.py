from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CalendarExam, ExamRuleRecord, SourceDocument
from app.extraction.schema import ExamRules
from app.sources.ssc_calendar import CalendarEntry
from app.storage.documents import CachedDocument


def upsert_document(session: Session, document: CachedDocument) -> SourceDocument:
    existing = session.scalar(
        select(SourceDocument).where(SourceDocument.sha256 == document.sha256)
    )
    if existing is None:
        existing = SourceDocument(sha256=document.sha256)
        session.add(existing)

    existing.source_id = document.source_id
    existing.title = document.title
    existing.origin_url = document.origin_url
    existing.relative_path = document.relative_path
    existing.byte_size = document.byte_size
    existing.page_count = document.page_count
    existing.kind = document.kind
    existing.kind_reason = document.kind_reason
    existing.fetched_at = document.fetched_at
    return existing


def upsert_rules(session: Session, rules: ExamRules) -> ExamRuleRecord:
    existing = session.scalar(
        select(ExamRuleRecord).where(
            ExamRuleRecord.document_sha256 == rules.document_sha256
        )
    )
    if existing is None:
        existing = ExamRuleRecord(document_sha256=rules.document_sha256)
        session.add(existing)

    existing.source_id = rules.source_id
    existing.exam_name = rules.exam_name
    existing.payload = rules.model_dump(mode="json")
    existing.is_readable = rules.age is not None or bool(rules.qualifications)
    return existing


def upsert_calendar(session: Session, entry: CalendarEntry) -> CalendarExam:
    existing = session.scalar(
        select(CalendarExam).where(
            CalendarExam.source_id == entry.source_id,
            CalendarExam.exam_name == entry.exam_name,
        )
    )
    if existing is None:
        existing = CalendarExam(source_id=entry.source_id, exam_name=entry.exam_name)
        session.add(existing)
    existing.payload = entry.model_dump(mode="json")
    return existing


def all_rules(session: Session) -> list[ExamRules]:
    records = session.scalars(select(ExamRuleRecord)).all()
    return [ExamRules.model_validate(r.payload) for r in records]


def all_calendar(session: Session) -> list[CalendarEntry]:
    records = session.scalars(select(CalendarExam)).all()
    return [CalendarEntry.model_validate(r.payload) for r in records]


def all_documents(session: Session) -> list[SourceDocument]:
    return list(session.scalars(select(SourceDocument).order_by(SourceDocument.source_id)).all())
