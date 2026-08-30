from __future__ import annotations

from app.eligibility.levels import (
    is_only_desirable,
    level_asked_for,
    satisfies,
    what_is_missing,
)
from app.eligibility.verdict import Reason
from app.extraction.schema import ExamRules, Qualification
from app.student.profile import StudentProfile
from app.student.qualifications import LEVEL_LABEL, Level


def _marks_for(student: StudentProfile, level: Level | None) -> float | None:
    if level is not None:
        from_ladder = student.education_history.percentage_at(level)
        if from_ladder is not None:
            return from_ladder
    return student.education.percentage


def _check_level(
    requirement: Qualification, student: StudentProfile
) -> tuple[Reason | None, Level | None]:
    needed = level_asked_for(requirement.requirement)
    if needed is None:
        return None, None

    highest = student.education_history.highest_completed
    if highest is None and student.education.is_completed:
        return None, needed

    if satisfies(highest, needed):
        return (
            Reason(
                text=(
                    f"This exam needs {LEVEL_LABEL[needed].lower()}. "
                    f"You have finished {LEVEL_LABEL[highest].lower()}, so that is fine."
                ),
                citation=requirement.citation,
            ),
            needed,
        )

    still_studying = any(
        entry.level is needed and not entry.is_completed
        for entry in student.education_history.entries
    )
    if still_studying:
        return (
            Reason(
                text=(
                    f"This exam needs {LEVEL_LABEL[needed].lower()}, and you have not "
                    "finished it yet. You can apply once you have."
                ),
                citation=requirement.citation,
                blocks_application=True,
            ),
            needed,
        )

    return (
        Reason(
            text=what_is_missing(needed, highest),
            citation=requirement.citation,
            blocks_application=True,
        ),
        needed,
    )


def _check_marks(
    requirement: Qualification, student: StudentProfile, level: Level | None
) -> Reason | None:
    needed = requirement.minimum_percentage
    if needed is None:
        return None

    have = _marks_for(student, level)
    where = LEVEL_LABEL[level].lower() if level else "your qualification"

    if have is None:
        return Reason(
            text=(
                f"This exam needs at least {needed:g}% in {where}. "
                "Add those marks to your profile so we can check."
            ),
            citation=requirement.citation,
            blocks_application=True,
        )

    if have < needed:
        return Reason(
            text=(
                f"This exam needs {needed:g}% in {where}. You have {have:g}%, "
                f"which is {needed - have:.1f}% short."
            ),
            citation=requirement.citation,
            blocks_application=True,
            is_permanent=True,
        )

    return Reason(
        text=f"Your {where} marks of {have:g}% clear the {needed:g}% this exam asks for.",
        citation=requirement.citation,
    )


def evaluate_qualification(rules: ExamRules, student: StudentProfile) -> list[Reason]:
    if not rules.qualifications:
        return []

    reasons: list[Reason] = []
    for requirement in rules.qualifications:
        quote = requirement.citation.quote if requirement.citation else ""
        if is_only_desirable(requirement.requirement, quote):
            reasons.append(
                Reason(
                    text=(
                        f"{requirement.requirement[:70]} is desirable, not required. "
                        "Not having it does not stop you applying."
                    ),
                    citation=requirement.citation,
                )
            )
            continue

        level_reason, level = _check_level(requirement, student)
        if level_reason:
            reasons.append(level_reason)

        marks_reason = _check_marks(requirement, student, level)
        if marks_reason:
            reasons.append(marks_reason)

        if level_reason is None and marks_reason is None:
            reasons.append(
                Reason(
                    text=(
                        "We could not tell which level this exam asks for. "
                        "Please read the notification yourself before applying."
                    ),
                    citation=requirement.citation,
                )
            )

    if not student.education.is_completed and not student.education_history.entries:
        reasons.append(
            Reason(text="You have not finished your qualification yet.", blocks_application=True)
        )
    return reasons
