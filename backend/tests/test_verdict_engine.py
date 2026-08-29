from __future__ import annotations

from datetime import date

import pytest

from app.eligibility.engine import decide
from app.eligibility.verdict import Bucket
from app.extraction.schema import (
    AgeRelaxation,
    AgeRule,
    ApplicationFee,
    Citation,
    ExamRules,
    Qualification,
)
from app.student.profile import Category, Education, Gender, StudentProfile

TODAY = date(2026, 8, 29)
CITE = Citation(page=6, quote="Minimum: 20 years Maximum: 30 years")


def make_rules(**overrides) -> ExamRules:
    base = dict(
        exam_name="Test Exam",
        source_id="test",
        document_sha256="deadbeef",
        age=AgeRule(minimum_years=20, maximum_years=30, reckoned_on=date(2026, 7, 1), citation=CITE),
        age_relaxations=[
            AgeRelaxation(category="Scheduled Caste/Scheduled Tribe", extra_years=5, citation=CITE),
            AgeRelaxation(category="Other Backward Classes (Non-Creamy Layer)", extra_years=3, citation=CITE),
        ],
        fees=[
            ApplicationFee(amount_rupees=175, applies_to="SC/ST/PwBD candidates", citation=CITE),
            ApplicationFee(amount_rupees=850, applies_to="all others", citation=CITE),
        ],
    )
    base.update(overrides)
    return ExamRules(**base)


def make_student(born: date, category: Category = Category.UR, **kw) -> StudentProfile:
    return StudentProfile(
        name="Test", date_of_birth=born, category=category,
        state="Maharashtra", district="Nagpur",
        education=Education(degree="B.Tech", percentage=kw.pop("percentage", 58.0)),
        **kw,
    )


def test_student_inside_the_window_can_apply():
    verdict = decide(make_rules(), make_student(date(2000, 1, 1)), TODAY)
    assert verdict.bucket is Bucket.APPLY_NOW


def test_too_young_is_not_yet_and_says_when():
    verdict = decide(make_rules(), make_student(date(2010, 5, 1)), TODAY)
    assert verdict.bucket is Bucket.NOT_YET
    assert "2030" in " ".join(r.text for r in verdict.blocking_reasons)


def test_too_old_is_permanent():
    verdict = decide(make_rules(), make_student(date(1985, 1, 1)), TODAY)
    assert verdict.bucket is Bucket.NOT_FOR_YOU
    assert any(r.is_permanent for r in verdict.blocking_reasons)


def test_obc_relaxation_saves_a_student_who_would_otherwise_be_barred():
    born = date(1994, 1, 1)
    general = decide(make_rules(), make_student(born, Category.UR), TODAY)
    obc = decide(make_rules(), make_student(born, Category.OBC), TODAY)

    assert general.bucket is Bucket.NOT_FOR_YOU
    assert obc.bucket is Bucket.APPLY_NOW
    assert obc.relaxation_applied == 3


def test_sc_gets_five_years_not_obc_three():
    verdict = decide(make_rules(), make_student(date(2000, 1, 1), Category.SC), TODAY)
    assert verdict.relaxation_applied == 5


def test_reserved_category_pays_the_lower_fee():
    sc = decide(make_rules(), make_student(date(2000, 1, 1), Category.SC), TODAY)
    ur = decide(make_rules(), make_student(date(2000, 1, 1), Category.UR), TODAY)
    assert sc.fee_payable == 175
    assert ur.fee_payable == 850


def test_percentage_shortfall_blocks_and_says_how_short():
    rules = make_rules(
        qualifications=[Qualification(requirement="Degree with 60%", minimum_percentage=60.0, citation=CITE)]
    )
    verdict = decide(rules, make_student(date(2000, 1, 1), percentage=58.0), TODAY)
    assert verdict.bucket is Bucket.NOT_FOR_YOU
    assert "2.0% short" in " ".join(r.text for r in verdict.reasons)


def test_every_verdict_reason_can_be_traced_to_the_pdf():
    verdict = decide(make_rules(), make_student(date(2000, 1, 1)), TODAY)
    cited = [r for r in verdict.reasons if r.citation]
    assert len(cited) >= 2
    for reason in cited:
        assert reason.citation.page > 0
