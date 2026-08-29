from __future__ import annotations

from datetime import date

from pydantic import BaseModel, computed_field

from app.eligibility.categories import best_relaxation_years
from app.extraction.schema import ExamRules
from app.student.profile import StudentProfile


class ClosingExam(BaseModel):
    exam_name: str
    source_id: str
    limit_for_you: int
    closes_on_birthday: int
    closes_on: date


class AgeCliff(BaseModel):
    student_name: str
    next_birthday: date
    turning: int
    exams_closing: list[ClosingExam] = []

    @computed_field
    @property
    def has_warning(self) -> bool:
        return bool(self.exams_closing)

    @computed_field
    @property
    def message(self) -> str:
        if not self.exams_closing:
            return "No exam closes to you because of your age yet."

        soonest = self.exams_closing[0]
        same_day = [e for e in self.exams_closing if e.closes_on == soonest.closes_on]
        when = soonest.closes_on.strftime("%d %B %Y")
        count = len(same_day)
        word = "exam closes" if count == 1 else "exams close"
        return (
            f"You turn {soonest.closes_on_birthday} on {when}. "
            f"That day {count} {word} to you permanently, and you cannot sit "
            f"{'it' if count == 1 else 'them'} again."
        )


def _next_birthday(student: StudentProfile, today: date) -> tuple[date, int]:
    birthday = student.date_of_birth
    this_year = date(today.year, birthday.month, birthday.day)
    if this_year >= today:
        return this_year, today.year - birthday.year
    return date(today.year + 1, birthday.month, birthday.day), today.year + 1 - birthday.year


def find_age_cliff(
    student: StudentProfile, rules_list: list[ExamRules], today: date, horizon_years: int = 1
) -> AgeCliff:
    next_birthday, turning = _next_birthday(student, today)
    horizon = date(next_birthday.year + horizon_years - 1, next_birthday.month, next_birthday.day)

    closing: list[ClosingExam] = []
    for rules in rules_list:
        if rules.age is None or rules.age.maximum_years is None:
            continue
        relaxation, _ = best_relaxation_years(
            [(r.category, r.extra_years) for r in rules.age_relaxations], student
        )
        limit = rules.age.maximum_years + relaxation
        age_now = student.age_on(today)
        if age_now > limit:
            continue

        closes_on = date(
            student.date_of_birth.year + limit + 1,
            student.date_of_birth.month,
            student.date_of_birth.day,
        )
        if today < closes_on <= horizon:
            closing.append(
                ClosingExam(
                    exam_name=rules.exam_name,
                    source_id=rules.source_id,
                    limit_for_you=limit,
                    closes_on_birthday=limit + 1,
                    closes_on=closes_on,
                )
            )

    closing.sort(key=lambda c: c.closes_on)
    return AgeCliff(
        student_name=student.name,
        next_birthday=next_birthday,
        turning=turning,
        exams_closing=closing,
    )
