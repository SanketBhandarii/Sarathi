from __future__ import annotations

from pydantic import BaseModel, computed_field

from app.eligibility.categories import label_applies_to
from app.extraction.schema import Citation, ExamRules
from app.student.profile import StudentProfile


class FeeSaving(BaseModel):
    exam_name: str
    source_id: str
    you_pay: float
    others_pay: float
    citation: Citation | None = None

    @computed_field
    @property
    def saved(self) -> float:
        return max(0.0, self.others_pay - self.you_pay)

    @computed_field
    @property
    def is_free_for_you(self) -> bool:
        return self.you_pay == 0

    @computed_field
    @property
    def plain_words(self) -> str:
        if self.is_free_for_you:
            return f"{self.exam_name}: you pay nothing. Others pay Rs {self.others_pay:.0f}."
        return (
            f"{self.exam_name}: you pay Rs {self.you_pay:.0f} instead of "
            f"Rs {self.others_pay:.0f}. That is Rs {self.saved:.0f} less."
        )


class SavingsSummary(BaseModel):
    student_name: str
    savings: list[FeeSaving] = []

    @computed_field
    @property
    def total_saved(self) -> float:
        return sum(s.saved for s in self.savings)

    @computed_field
    @property
    def message(self) -> str:
        if not self.savings:
            return "You do not get a fee concession on the exams we are watching."
        count = len(self.savings)
        word = "exam" if count == 1 else "exams"
        return (
            f"You pay less on {count} {word}. Altogether that is "
            f"Rs {self.total_saved:.0f} you do not have to pay."
        )


def find_savings(student: StudentProfile, rules_list: list[ExamRules]) -> SavingsSummary:
    savings: list[FeeSaving] = []

    for rules in rules_list:
        if len(rules.fees) < 2:
            continue
        mine = [f for f in rules.fees if label_applies_to(f.applies_to, student)]
        if not mine:
            continue

        yours = min(mine, key=lambda f: f.amount_rupees)
        highest = max(rules.fees, key=lambda f: f.amount_rupees)
        if yours.amount_rupees >= highest.amount_rupees:
            continue

        savings.append(
            FeeSaving(
                exam_name=rules.exam_name,
                source_id=rules.source_id,
                you_pay=yours.amount_rupees,
                others_pay=highest.amount_rupees,
                citation=yours.citation,
            )
        )

    savings.sort(key=lambda s: -s.saved)
    return SavingsSummary(student_name=student.name, savings=savings)
