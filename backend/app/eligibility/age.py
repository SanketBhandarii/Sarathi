from __future__ import annotations

from datetime import date

from app.eligibility.categories import best_relaxation_years
from app.eligibility.verdict import Reason
from app.extraction.schema import ExamRules
from app.student.profile import StudentProfile


def _years_phrase(years: float) -> str:
    return f"{years:.0f}"


def evaluate_age(
    rules: ExamRules, student: StudentProfile, today: date
) -> tuple[list[Reason], int, str | None]:
    if rules.age is None:
        return [
            Reason(text="We could not read the age rule from this notification.")
        ], 0, None

    reckoned_on = rules.age.reckoned_on or today
    age = student.age_on(reckoned_on)
    citation = rules.age.citation

    relaxation, label = best_relaxation_years(
        [(r.category, r.extra_years) for r in rules.age_relaxations], student
    )

    reasons: list[Reason] = []
    if relaxation:
        reasons.append(
            Reason(
                text=f"You get {relaxation} extra years because you are {student.category.value}.",
                citation=next(
                    (r.citation for r in rules.age_relaxations if r.category == label), None
                ),
            )
        )

    minimum = rules.age.minimum_years
    maximum = rules.age.maximum_years
    effective_max = maximum + relaxation if maximum is not None else None

    if minimum is not None and age < minimum:
        eligible_from = student.turns(minimum)
        reasons.append(
            Reason(
                text=(
                    f"You are {_years_phrase(age)}. This exam needs at least {minimum}. "
                    f"You can apply from {eligible_from.strftime('%d %B %Y')}."
                ),
                citation=citation,
                blocks_application=True,
            )
        )
        return reasons, relaxation, label

    if effective_max is not None and age > effective_max:
        reasons.append(
            Reason(
                text=(
                    f"You are {_years_phrase(age)}. The limit for you is {effective_max}. "
                    "This exam is closed to you permanently."
                ),
                citation=citation,
                blocks_application=True,
                is_permanent=True,
            )
        )
        return reasons, relaxation, label

    if effective_max is not None:
        last_day = student.turns(effective_max + 1)
        reasons.append(
            Reason(
                text=(
                    f"Your age is fine. You are {_years_phrase(age)} and the limit for you "
                    f"is {effective_max}. You cross that limit when you turn "
                    f"{effective_max + 1} on {last_day.strftime('%d %B %Y')}."
                ),
                citation=citation,
            )
        )
    return reasons, relaxation, label
