from __future__ import annotations

import re
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_student_or_404
from app.core.config import get_settings
from app.db.models import SourceDocument, Student
from app.exams.naming import name_for
from app.extraction.document import has_readable_text, load_pages
from app.storage.cache import NotificationCache

router = APIRouter(prefix="/students", tags=["changes"])

CORRECTION_WORDS = (
    r"corrigend",
    r"notice regarding change",
    r"amendment",
    r"revised",
    r"change in recruitment",
    r"addendum",
)


class PublishedCorrection(BaseModel):
    exam_name: str
    official_title: str
    body: str
    source_id: str
    origin_url: str
    fetched_on: date
    we_could_read_it: bool
    what_we_can_say: str


def _looks_like_a_correction(title: str) -> bool:
    return any(re.search(word, title, re.IGNORECASE) for word in CORRECTION_WORDS)


@router.get("/{student_id}/changes", response_model=list[PublishedCorrection])
def read_changes(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
) -> list[PublishedCorrection]:
    settings = get_settings()
    cache = NotificationCache(settings.notifications_path)

    found: list[PublishedCorrection] = []
    for document in db.scalars(select(SourceDocument)).all():
        if not _looks_like_a_correction(document.title):
            continue

        cached = cache.index.by_hash().get(document.sha256)
        readable = False
        if cached is not None:
            readable = has_readable_text(load_pages(cached.path_under(cache.root)))

        named = name_for(document.title, document.source_id)
        found.append(
            PublishedCorrection(
                exam_name=named.short,
                official_title=named.full,
                body=named.body_full,
                source_id=document.source_id,
                origin_url=document.origin_url,
                fetched_on=document.fetched_at.date(),
                we_could_read_it=readable,
                what_we_can_say=(
                    "Sarathi has read this one and will tell you exactly what changed."
                    if readable
                    else (
                        "The commission published this as a photograph of paper, so Sarathi "
                        "cannot read what changed. It will not guess. Open the notice and "
                        "read it yourself."
                    )
                ),
            )
        )

    found.sort(key=lambda c: c.fetched_on, reverse=True)
    return found
