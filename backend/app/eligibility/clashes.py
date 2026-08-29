from __future__ import annotations

from collections import defaultdict
from datetime import date

from pydantic import BaseModel, computed_field

from app.eligibility.radar import Radar
from app.eligibility.verdict import Bucket


class ExamOnDay(BaseModel):
    exam_name: str
    source_id: str
    you_can_apply: bool


class Clash(BaseModel):
    happens_on: date
    exams: list[ExamOnDay]

    @computed_field
    @property
    def plain_words(self) -> str:
        names = " and ".join(e.exam_name[:44] for e in self.exams[:2])
        extra = "" if len(self.exams) <= 2 else f" and {len(self.exams) - 2} more"
        when = self.happens_on.strftime("%d %B %Y")
        return f"{names}{extra} are both on {when}. You can sit only one."


def find_clashes(radar: Radar, today: date) -> list[Clash]:
    by_day: dict[date, list[ExamOnDay]] = defaultdict(list)

    for entry in radar.entries:
        if entry.closing_on is None or entry.closing_on < today:
            continue
        if entry.closing_is_month_only:
            continue
        by_day[entry.closing_on].append(
            ExamOnDay(
                exam_name=entry.exam_name,
                source_id=entry.source_id,
                you_can_apply=entry.bucket is Bucket.APPLY_NOW,
            )
        )

    return [
        Clash(happens_on=day, exams=exams)
        for day, exams in sorted(by_day.items())
        if len(exams) > 1
    ]
