from __future__ import annotations

from app.eligibility.verdict import Reason
from app.extraction.schema import ExamRules
from app.student.profile import StudentProfile


def evaluate_qualification(rules: ExamRules, student: StudentProfile) -> list[Reason]:
    if not rules.qualifications:
        return []

    reasons: list[Reason] = []
    for requirement in rules.qualifications:
        needed = requirement.minimum_percentage
        if needed is None:
            continue
        if student.education.percentage is None:
            reasons.append(
                Reason(
                    text=(
                        f"This exam needs at least {needed:g}%. "
                        "Add your marks to your profile so we can check this."
                    ),
                    citation=requirement.citation,
                    blocks_application=True,
                )
            )
        elif student.education.percentage < needed:
            short_by = needed - student.education.percentage
            reasons.append(
                Reason(
                    text=(
                        f"This exam needs {needed:g}%. You have "
                        f"{student.education.percentage:g}%, which is {short_by:.1f}% short."
                    ),
                    citation=requirement.citation,
                    blocks_application=True,
                    is_permanent=True,
                )
            )

    if not student.education.is_completed:
        reasons.append(
            Reason(
                text="You have not finished your degree yet.",
                blocks_application=True,
            )
        )

    if not reasons and rules.qualifications:
        first = rules.qualifications[0]
        reasons.append(
            Reason(
                text=f"Your {student.education.degree} meets what this exam asks for.",
                citation=first.citation,
            )
        )
    return reasons
