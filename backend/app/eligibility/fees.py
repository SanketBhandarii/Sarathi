from __future__ import annotations

from app.eligibility.categories import label_applies_to
from app.eligibility.verdict import Reason
from app.extraction.schema import ExamRules
from app.student.profile import StudentProfile


def evaluate_fee(
    rules: ExamRules, student: StudentProfile
) -> tuple[float | None, bool, list[Reason]]:
    if not rules.fees:
        return None, False, []

    matched = [f for f in rules.fees if label_applies_to(f.applies_to, student)]
    chosen = min(matched, key=lambda f: f.amount_rupees) if matched else max(
        rules.fees, key=lambda f: f.amount_rupees
    )

    cheapest = min(rules.fees, key=lambda f: f.amount_rupees)
    waived = chosen.amount_rupees == 0

    reasons: list[Reason] = []
    if waived:
        reasons.append(
            Reason(
                text="You do not have to pay the fee for this exam.",
                citation=chosen.citation,
            )
        )
    elif matched and chosen.amount_rupees < max(f.amount_rupees for f in rules.fees):
        saving = max(f.amount_rupees for f in rules.fees) - chosen.amount_rupees
        reasons.append(
            Reason(
                text=(
                    f"You pay Rs {chosen.amount_rupees:.0f} instead of "
                    f"Rs {max(f.amount_rupees for f in rules.fees):.0f}. "
                    f"That is Rs {saving:.0f} less."
                ),
                citation=chosen.citation,
            )
        )
    else:
        reasons.append(
            Reason(text=f"The fee is Rs {chosen.amount_rupees:.0f}.", citation=chosen.citation)
        )

    return chosen.amount_rupees, waived, reasons
