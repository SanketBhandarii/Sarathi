from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel

from app.extraction.schema import Citation, ExamRules
from app.student.profile import StudentProfile


class Bucket(StrEnum):
    APPLY_NOW = "apply_now"
    COMING_SOON = "coming_soon"
    NOT_YET = "not_yet"
    NOT_FOR_YOU = "not_for_you"
    UNKNOWN = "unknown"


BUCKET_LABEL: dict[Bucket, str] = {
    Bucket.APPLY_NOW: "You can apply now",
    Bucket.COMING_SOON: "You can apply, form not open yet",
    Bucket.NOT_YET: "Not yet",
    Bucket.NOT_FOR_YOU: "Not for you",
    Bucket.UNKNOWN: "We could not check this one",
}


class Reason(BaseModel):
    text: str
    citation: Citation | None = None
    blocks_application: bool = False
    is_permanent: bool = False


class ExamVerdict(BaseModel):
    exam_name: str
    source_id: str
    bucket: Bucket
    reasons: list[Reason] = []
    fee_payable: float | None = None
    fee_waived: bool = False
    relaxation_applied: int = 0
    relaxation_label: str | None = None
    unchecked: list[str] = []

    @property
    def headline(self) -> str:
        return BUCKET_LABEL[self.bucket]

    @property
    def blocking_reasons(self) -> list[Reason]:
        return [r for r in self.reasons if r.blocks_application]
