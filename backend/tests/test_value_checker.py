from __future__ import annotations

import json

import pytest

from app.core.config import get_settings
from app.extraction.review import check_values, numbers_in, unsupported_values
from app.extraction.store import ExamRulesStore


@pytest.fixture(scope="module")
def rules():
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if "CRP-PO" in d["title"])
    found = ExamRulesStore(settings.exams_path).get(doc["sha256"])
    if found is None:
        pytest.skip("run scripts.extract_one first")
    return found


def test_numbers_in_reads_plain_and_comma_numbers():
    assert numbers_in("Rs 1,750 and 30 years") == (1750.0, 30.0)


def test_every_real_value_appears_in_its_own_quote(rules):
    assert unsupported_values(check_values(rules)) == []


def test_inflated_age_is_caught(rules):
    tampered = rules.model_copy(deep=True)
    tampered.age.maximum_years = 45
    caught = {c.field for c in unsupported_values(check_values(tampered))}
    assert "age.maximum_years" in caught


def test_inflated_relaxation_is_caught(rules):
    tampered = rules.model_copy(deep=True)
    for item in tampered.age_relaxations:
        item.extra_years = 99
    assert len(unsupported_values(check_values(tampered))) == len(tampered.age_relaxations)


def test_wrong_fee_is_caught(rules):
    tampered = rules.model_copy(deep=True)
    if not tampered.fees:
        pytest.skip("no fees extracted")
    tampered.fees[0].amount_rupees = 12345.0
    caught = [c for c in unsupported_values(check_values(tampered))]
    assert any(c.value == 12345.0 for c in caught)
