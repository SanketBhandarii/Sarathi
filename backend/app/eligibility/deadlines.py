from __future__ import annotations

from datetime import date

from pydantic import BaseModel, computed_field

from app.eligibility.radar import Radar
from app.exams.naming import name_for
from app.eligibility.verdict import Bucket


class UpcomingDeadline(BaseModel):
    exam_name: str
    source_id: str
    label: str
    due_on: date
    days_left: int
    is_approximate: bool
    you_can_apply: bool
    citation_page: int | None = None
    citation_quote: str | None = None

    @computed_field
    @property
    def urgency(self) -> str:
        if self.days_left <= 3:
            return "today"
        if self.days_left <= 10:
            return "this week"
        if self.days_left <= 30:
            return "this month"
        return "later"

    @computed_field
    @property
    def plain_words(self) -> str:
        if self.days_left == 0:
            return f"{self.exam_name}: last day to apply is today."
        if self.days_left == 1:
            return f"{self.exam_name}: last day to apply is tomorrow."
        return (
            f"{self.exam_name}: {self.days_left} days left to apply, "
            f"closes {self.due_on.strftime('%d %B %Y')}."
        )


def upcoming_deadlines(radar: Radar, today: date, within_days: int = 120) -> list[UpcomingDeadline]:
    found: list[UpcomingDeadline] = []

    for entry in radar.entries:
        if entry.closing_on is None:
            continue
        days_left = (entry.closing_on - today).days
        if days_left < 0 or days_left > within_days:
            continue

        citation = next(
            (r.citation for r in entry.reasons if r.citation and "date" in r.text.lower()),
            None,
        )
        found.append(
            UpcomingDeadline(
                exam_name=name_for(entry.exam_name, entry.source_id).short,
                source_id=entry.source_id,
                label="Last date to apply",
                due_on=entry.closing_on,
                days_left=days_left,
                is_approximate=entry.closing_is_month_only,
                you_can_apply=entry.bucket is Bucket.APPLY_NOW,
                citation_page=citation.page if citation else None,
                citation_quote=citation.quote if citation else None,
            )
        )

    found.sort(key=lambda d: d.due_on)
    return found
