from __future__ import annotations

import json

import pytest

from agents import pipeline
from app.core.config import get_settings
from app.extraction.document import load_pages
from app.extraction.schema import AgeSection
from app.extraction.store import ExamRulesStore


@pytest.fixture(scope="module")
def fixture_data():
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if "CRP-PO" in d["title"])
    rules = ExamRulesStore(settings.exams_path).get(doc["sha256"])
    if rules is None:
        pytest.skip("run scripts.process_document first")
    pages = load_pages(settings.notifications_path / doc["relative_path"])
    return rules, pages, doc


def test_loop_stops_immediately_when_first_attempt_is_clean(monkeypatch, fixture_data):
    rules, pages, doc = fixture_data
    calls = {"extract": 0}

    def fake_extract_rules(*args, **kwargs):
        calls["extract"] += 1
        return rules.model_copy(deep=True)

    monkeypatch.setattr(pipeline.extractor, "extract_rules", fake_extract_rules)
    result = pipeline.extract_and_verify(
        pages, doc["title"], doc["source_id"], doc["sha256"], use_model_review=False
    )

    assert result.attempts == 1
    assert result.trustworthy
    assert calls["extract"] == 1


def test_loop_retries_and_recovers_from_a_bad_first_reading(monkeypatch, fixture_data):
    rules, pages, doc = fixture_data
    good_age = AgeSection(age=rules.age, relaxations=rules.age_relaxations)

    broken = rules.model_copy(deep=True)
    broken.age.maximum_years = 45

    attempts = {"age": 0}

    def fake_extract_rules(*args, **kwargs):
        return broken.model_copy(deep=True)

    def fake_extract_age(pages_arg, extra_instruction=""):
        attempts["age"] += 1
        assert "45" in extra_instruction or "maximum_years" in extra_instruction
        return good_age.model_copy(deep=True)

    monkeypatch.setattr(pipeline.extractor, "extract_rules", fake_extract_rules)
    monkeypatch.setattr(pipeline.extractor, "extract_age", fake_extract_age)

    result = pipeline.extract_and_verify(
        pages, doc["title"], doc["source_id"], doc["sha256"], use_model_review=False
    )

    assert attempts["age"] == 1
    assert result.attempts == 2
    assert result.trustworthy
    assert result.rules.age.maximum_years == 30


def test_unfixable_claim_is_dropped_not_shown(monkeypatch, fixture_data):
    rules, pages, doc = fixture_data
    broken = rules.model_copy(deep=True)
    broken.age.maximum_years = 45
    broken_age = AgeSection(age=broken.age, relaxations=broken.age_relaxations)

    monkeypatch.setattr(pipeline.extractor, "extract_rules", lambda *a, **k: broken.model_copy(deep=True))
    monkeypatch.setattr(pipeline.extractor, "extract_age", lambda *a, **k: broken_age.model_copy(deep=True))

    result = pipeline.extract_and_verify(
        pages, doc["title"], doc["source_id"], doc["sha256"],
        max_attempts=3, use_model_review=False,
    )

    assert result.attempts == 3
    assert len(result.history) == 4

    assert result.rules.age.maximum_years is None
    assert "age.maximum_years" in result.rules.could_not_verify
    assert result.trustworthy
