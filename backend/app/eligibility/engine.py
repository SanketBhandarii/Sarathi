from __future__ import annotations

from datetime import date
from enum import StrEnum

from app.eligibility.age import evaluate_age
from app.eligibility.fees import evaluate_fee
from app.eligibility.layers import domicile_blocks
from app.eligibility.qualification import evaluate_qualification
from app.eligibility.verdict import Bucket, ExamVerdict, Reason
from app.extraction.schema import ExamRules
from app.student.profile import StudentProfile


class Window(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    NOT_KNOWN = "not_known"


def _window_state(rules: ExamRules, today: date) -> tuple[Window, Reason | None]:
    closing = [d for d in rules.key_dates if "last" in d.label.lower() or "clos" in d.label.lower()]
    if not closing:
        return Window.NOT_KNOWN, Reason(
            text=(
                "We could not find the last date to apply anywhere in this notification, "
                "so we will not tell you it is open. Open the official page and check the "
                "date yourself before you plan around it."
            )
        )

    last_date = min(d.happens_on for d in closing)
    entry = next(d for d in closing if d.happens_on == last_date)
    if last_date < today:
        return Window.CLOSED, Reason(
            text=f"The form closed on {last_date.strftime('%d %B %Y')}.",
            citation=entry.citation,
        )

    days_left = (last_date - today).days
    return Window.OPEN, Reason(
        text=f"Last date to apply is {last_date.strftime('%d %B %Y')}, {days_left} days from now.",
        citation=entry.citation,
    )


def decide(rules: ExamRules, student: StudentProfile, today: date | None = None) -> ExamVerdict:
    today = today or date.today()

    if rules.age is None and not rules.qualifications:
        return ExamVerdict(
            exam_name=rules.exam_name,
            source_id=rules.source_id,
            bucket=Bucket.UNKNOWN,
            reasons=[Reason(text="We could not read the rules for this exam clearly.")],
            unchecked=rules.could_not_verify,
        )

    domicile_problem = domicile_blocks(rules.source_id, student)
    if domicile_problem:
        return ExamVerdict(
            exam_name=rules.exam_name,
            source_id=rules.source_id,
            bucket=Bucket.NOT_FOR_YOU,
            reasons=[
                Reason(text=domicile_problem, blocks_application=True, is_permanent=True)
            ],
            unchecked=rules.could_not_verify,
        )

    age_reasons, relaxation, label = evaluate_age(rules, student, today)
    qualification_reasons = evaluate_qualification(rules, student)
    fee_amount, fee_waived, fee_reasons = evaluate_fee(rules, student)
    window, window_reason = _window_state(rules, today)

    reasons = _without_repeats(age_reasons + qualification_reasons)
    blocking = [r for r in reasons if r.blocks_application]

    if blocking:
        permanent = any(r.is_permanent for r in blocking)
        bucket = Bucket.NOT_FOR_YOU if permanent else Bucket.NOT_YET
    elif window is Window.CLOSED:
        bucket = Bucket.CLOSED_FOR_NOW
    elif window is Window.NOT_KNOWN:
        bucket = Bucket.UNKNOWN
    else:
        bucket = Bucket.APPLY_NOW

    if window_reason:
        reasons = reasons + [window_reason]
    if bucket in (Bucket.APPLY_NOW, Bucket.COMING_SOON):
        reasons = reasons + fee_reasons

    return ExamVerdict(
        exam_name=rules.exam_name,
        source_id=rules.source_id,
        bucket=bucket,
        reasons=reasons,
        fee_payable=fee_amount,
        fee_waived=fee_waived,
        relaxation_applied=relaxation,
        relaxation_label=label,
        unchecked=rules.could_not_verify,
    )


def _without_repeats(reasons: list[Reason]) -> list[Reason]:
    kept: list[Reason] = []
    said: set[str] = set()
    for reason in reasons:
        if reason.text in said:
            continue
        said.add(reason.text)
        kept.append(reason)
    return kept
