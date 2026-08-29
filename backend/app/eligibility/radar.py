from __future__ import annotations

from calendar import monthrange
from datetime import date

from pydantic import BaseModel

from app.eligibility.engine import decide
from app.eligibility.layers import Layer, layer_for
from app.eligibility.verdict import BUCKET_LABEL, Bucket, ExamVerdict, Reason
from app.extraction.schema import ExamRules
from app.sources.ssc_calendar import CalendarEntry
from app.student.profile import StudentProfile


class RadarEntry(BaseModel):
    exam_name: str
    source_id: str
    bucket: Bucket
    reasons: list[Reason] = []
    rules_known: bool
    layer: Layer = Layer.CENTRAL
    closing_text: str | None = None
    closing_on: date | None = None
    closing_is_month_only: bool = False
    fee_payable: float | None = None
    unchecked: list[str] = []

    @property
    def headline(self) -> str:
        return BUCKET_LABEL[self.bucket]


class Radar(BaseModel):
    student_name: str
    generated_on: date
    entries: list[RadarEntry] = []

    def bucket(self, bucket: Bucket) -> list[RadarEntry]:
        return [e for e in self.entries if e.bucket is bucket]

    def counts(self) -> dict[Bucket, int]:
        return {b: len(self.bucket(b)) for b in Bucket}

    def layer(self, layer: Layer) -> list[RadarEntry]:
        return [e for e in self.entries if e.layer is layer]


def _from_verdict(verdict: ExamVerdict, rules: ExamRules, student: StudentProfile) -> RadarEntry:
    closing = [d for d in rules.key_dates if "last" in d.label.lower() or "clos" in d.label.lower()]
    closes_on = min((d.happens_on for d in closing), default=None)
    return RadarEntry(
        exam_name=verdict.exam_name,
        source_id=verdict.source_id,
        bucket=verdict.bucket,
        reasons=verdict.reasons,
        rules_known=True,
        layer=layer_for(verdict.source_id, student),
        closing_on=closes_on,
        closing_text=closes_on.strftime("%d %B %Y") if closes_on else None,
        fee_payable=verdict.fee_payable,
        unchecked=verdict.unchecked,
    )


def _latest_possible(entry: CalendarEntry) -> date | None:
    if entry.closes_on is None:
        return None
    if not entry.closes_is_month_only:
        return entry.closes_on
    last_day = monthrange(entry.closes_on.year, entry.closes_on.month)[1]
    return entry.closes_on.replace(day=last_day)


def _from_calendar(entry: CalendarEntry, today: date, student: StudentProfile) -> RadarEntry:
    shown = entry.closes_text if entry.closes_is_month_only else (
        entry.closes_on.strftime("%d %B %Y") if entry.closes_on else None
    )
    deadline = _latest_possible(entry)
    already_closed = deadline is not None and deadline < today

    if already_closed and entry.closes_is_month_only:
        reason_text = f"The form was due to close in {shown}, which has passed."
    elif already_closed:
        reason_text = f"The form closed on {shown}."
    elif shown:
        reason_text = f"The form is expected around {shown}."
    else:
        reason_text = "Dates not announced yet."
    return RadarEntry(
        exam_name=entry.exam_name,
        source_id=entry.source_id,
        bucket=Bucket.CLOSED_FOR_NOW if already_closed else Bucket.COMING_SOON,
        reasons=[
            Reason(text=reason_text),
            Reason(
                text="This exam runs every year. We will tell you when the next one opens."
                if already_closed
                else "We will check if you qualify when the notification is published."
            ),
        ],
        rules_known=False,
        layer=layer_for(entry.source_id, student),
        closing_on=entry.closes_on,
        closing_text=shown,
        closing_is_month_only=entry.closes_is_month_only,
    )


def build_radar(
    student: StudentProfile,
    rules_list: list[ExamRules],
    calendar: list[CalendarEntry],
    today: date | None = None,
) -> Radar:
    today = today or date.today()
    entries = [_from_verdict(decide(r, student, today), r, student) for r in rules_list]

    known = {e.exam_name.lower() for e in entries}
    entries.extend(
        _from_calendar(c, today, student) for c in calendar if c.exam_name.lower() not in known
    )

    order = {
        Bucket.APPLY_NOW: 0,
        Bucket.COMING_SOON: 1,
        Bucket.NOT_YET: 2,
        Bucket.CLOSED_FOR_NOW: 3,
        Bucket.UNKNOWN: 4,
        Bucket.NOT_FOR_YOU: 5,
    }
    entries.sort(key=lambda e: (order[e.bucket], e.closing_on or date.max))
    return Radar(student_name=student.name, generated_on=today, entries=entries)
