from __future__ import annotations

from datetime import date

import pytest

from app.eligibility.engine import decide
from app.eligibility.layers import Layer, domicile_blocks, layer_for
from app.eligibility.verdict import Bucket
from app.extraction.schema import AgeRule, Citation, ExamRules
from app.student.profile import Category, Education, StudentProfile

CITE = Citation(page=1, quote="Minimum: 20 years Maximum: 30 years")


def student_from(state: str, district: str) -> StudentProfile:
    return StudentProfile(
        name="Test", date_of_birth=date(2000, 1, 1), category=Category.OBC,
        state=state, district=district,
        education=Education(degree="B.Tech", percentage=58.0),
    )


MAHARASHTRA = student_from("Maharashtra", "Nagpur")
BIHAR = student_from("Bihar", "Patna")


@pytest.mark.parametrize("source_id", ["ssc", "upsc", "ibps"])
def test_central_exams_are_central_for_everyone(source_id):
    assert layer_for(source_id, MAHARASHTRA) is Layer.CENTRAL
    assert layer_for(source_id, BIHAR) is Layer.CENTRAL


def test_central_exams_never_block_on_domicile():
    for source_id in ("ssc", "upsc", "ibps"):
        assert domicile_blocks(source_id, BIHAR) is None


def test_state_exam_is_your_state_for_a_local_student():
    assert layer_for("mpsc", MAHARASHTRA) is Layer.YOUR_STATE
    assert domicile_blocks("mpsc", MAHARASHTRA) is None


def test_state_exam_is_another_state_for_an_outsider():
    assert layer_for("mpsc", BIHAR) is Layer.ANOTHER_STATE
    message = domicile_blocks("mpsc", BIHAR)
    assert message is not None
    assert "Maharashtra" in message and "Bihar" in message


def test_city_body_is_your_city_for_a_local_student():
    assert layer_for("bmc", MAHARASHTRA) is Layer.YOUR_CITY


def test_domicile_makes_the_verdict_not_for_you():
    rules = ExamRules(
        exam_name="MPSC State Services", source_id="mpsc", document_sha256="abc",
        age=AgeRule(minimum_years=19, maximum_years=38, citation=CITE),
    )
    local = decide(rules, MAHARASHTRA, date(2026, 8, 29))
    outsider = decide(rules, BIHAR, date(2026, 8, 29))

    assert local.bucket is Bucket.APPLY_NOW
    assert outsider.bucket is Bucket.NOT_FOR_YOU
    assert any(r.is_permanent for r in outsider.blocking_reasons)
