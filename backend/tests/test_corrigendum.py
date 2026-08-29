from __future__ import annotations

from datetime import date

from app.corrigendum.compare import compare
from app.corrigendum.diff import ChangeKind
from app.extraction.schema import (
    AgeRelaxation,
    AgeRule,
    ApplicationFee,
    Citation,
    ExamRules,
    KeyDate,
)

CITE = Citation(page=1, quote="Last date for online registration: 08.09.2026")
NEW_CITE = Citation(page=1, quote="CORRIGENDUM: last date revised to 02.09.2026")


def version(last_date: date, fee: float = 850, obc_years: int = 3, sha: str = "v1") -> ExamRules:
    return ExamRules(
        exam_name="Bank Exam", source_id="ibps", document_sha256=sha,
        age=AgeRule(minimum_years=20, maximum_years=30, citation=CITE),
        age_relaxations=[
            AgeRelaxation(category="Other Backward Classes", extra_years=obc_years, citation=CITE)
        ],
        fees=[ApplicationFee(amount_rupees=fee, applies_to="all others", citation=CITE)],
        key_dates=[KeyDate(label="Last date to apply", happens_on=last_date, citation=CITE)],
    )


def test_identical_versions_report_nothing():
    result = compare(version(date(2026, 9, 8)), version(date(2026, 9, 8), sha="v2"))
    assert result.has_changes is False
    assert "Nothing has changed" in result.apology


def test_a_date_moving_earlier_is_flagged_as_worse():
    result = compare(version(date(2026, 9, 8)), version(date(2026, 9, 2), sha="v2"))
    moved = [c for c in result.changes if c.kind is ChangeKind.DATE_MOVED]
    assert moved
    assert moved[0].is_worse_for_student is True
    assert "less time" in moved[0].plain_words


def test_a_date_moving_later_is_not_worse():
    result = compare(version(date(2026, 9, 8)), version(date(2026, 9, 20), sha="v2"))
    moved = [c for c in result.changes if c.kind is ChangeKind.DATE_MOVED]
    assert moved[0].is_worse_for_student is False


def test_the_agent_says_it_was_wrong():
    result = compare(version(date(2026, 9, 8)), version(date(2026, 9, 2), sha="v2"))
    assert "I was wrong" in result.apology


def test_fee_and_relaxation_changes_are_caught():
    result = compare(
        version(date(2026, 9, 8)),
        version(date(2026, 9, 8), fee=1000, obc_years=5, sha="v2"),
    )
    kinds = {c.kind for c in result.changes}
    assert ChangeKind.FEE_CHANGED in kinds
    assert ChangeKind.RELAXATION_CHANGED in kinds


def test_dates_are_shown_in_words_a_student_can_read():
    result = compare(version(date(2026, 9, 8)), version(date(2026, 9, 2), sha="v2"))
    moved = [c for c in result.changes if c.kind is ChangeKind.DATE_MOVED][0]
    assert "08 September 2026" in moved.plain_words
    assert "02 September 2026" in moved.plain_words


def test_a_removed_rule_is_reported():
    old = version(date(2026, 9, 8))
    new = version(date(2026, 9, 8), sha="v2")
    new.age_relaxations = []
    result = compare(old, new)
    assert any(c.kind is ChangeKind.RULE_REMOVED for c in result.changes)
