from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_student_or_404
from app.api.schemas import CitationOut, RadarEntryOut, RadarOut, ReasonOut
from app.db.models import Student
from sqlalchemy import select

from app.db.models import SourceDocument
from app.db.repositories import documents as docs_repo
from app.db.repositories import students as students_repo
from app.language.phrases import Language
from app.language.render import bucket_label, layer_label
from app.eligibility.layers import LAYER_LABEL
from app.eligibility.radar import RadarEntry, build_radar
from app.exams.naming import name_for

router = APIRouter(prefix="/students", tags=["radar"])


def _reason_out(reason) -> ReasonOut:
    return ReasonOut(
        text=reason.text,
        citation=CitationOut(page=reason.citation.page, quote=reason.citation.quote)
        if reason.citation
        else None,
        blocks_application=reason.blocks_application,
        is_permanent=reason.is_permanent,
    )


def _entry_out(
    entry: RadarEntry, language: Language, links: dict[str, tuple[str, str]]
) -> RadarEntryOut:
    link = links.get(entry.exam_name)
    named = name_for(entry.exam_name, entry.source_id)
    return RadarEntryOut(
        exam_name=named.short,
        official_title=named.full,
        body=named.body,
        body_full=named.body_full,
        source_id=entry.source_id,
        bucket=entry.bucket,
        headline=bucket_label(entry.bucket, language),
        layer=entry.layer,
        layer_label=layer_label(entry.layer, language),
        reasons=[_reason_out(r) for r in entry.reasons],
        rules_known=entry.rules_known,
        official_url=link[0] if link else None,
        document_title=link[1] if link else None,
        closing_text=entry.closing_text,
        closing_on=entry.closing_on,
        fee_payable=entry.fee_payable,
        unchecked=entry.unchecked,
    )


@router.get("/{student_id}/radar", response_model=RadarOut)
def read_radar(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
    today: date | None = Query(default=None),
    lang: Language = Query(default=Language.ENGLISH),
) -> RadarOut:
    profile = students_repo.to_profile(student)
    documents = db.scalars(select(SourceDocument)).all()
    links = {d.title: (d.origin_url, d.title) for d in documents}
    radar = build_radar(
        profile,
        docs_repo.all_rules(db),
        docs_repo.all_calendar(db),
        today=today or date.today(),
    )
    return RadarOut(
        language=lang,
        student_name=radar.student_name,
        generated_on=radar.generated_on,
        total_watched=len(radar.entries),
        counts={b.value: n for b, n in radar.counts().items() if n},
        entries=[_entry_out(e, lang, links) for e in radar.entries],
    )
