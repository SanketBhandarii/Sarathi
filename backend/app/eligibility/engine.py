from __future__ import annotations

from datetime import date

from app.eligibility.age import evaluate_age
from app.eligibility.fees import evaluate_fee
from app.eligibility.qualification import evaluate_qualification
from app.eligibility.verdict import Bucket, ExamVerdict, Reason
from app.extraction.schema import ExamRules
from app.student.profile import StudentProfile


def _window_state(rules: ExamRules, today: date) -> tuple[bool, Reason | None]:
    closing = [d for d in rules.key_dates if "last" in d.label.lower() or "clos" in d.label.lower()]
    if not closing:
        return True, None

    last_date = min(d.happens_on for d in closing)
    entry = next(d for d in closing if d.happens_on == last_date)
    if last_date < today:
        return False, Reason(
            text=f"The form closed on {last_date.strftime('%d %B %Y')}.",
            citation=entry.citation,
        )

    days_left = (last_date - today).days
    return True, Reason(
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

    age_reasons, relaxation, label = evaluate_age(rules, student, today)
    qualification_reasons = evaluate_qualification(rules, student)
    fee_amount, fee_waived, fee_reasons = evaluate_fee(rules, student)
    window_open, window_reason = _window_state(rules, today)

    reasons = age_reasons + qualification_reasons
    blocking = [r for r in reasons if r.blocks_application]

    if blocking:
        permanent = any(r.is_permanent for r in blocking)
        bucket = Bucket.NOT_FOR_YOU if permanent else Bucket.NOT_YET
    elif not window_open:
        bucket = Bucket.NOT_FOR_YOU
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
