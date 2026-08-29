from __future__ import annotations

import json

import pytest

from app.core.config import get_settings
from app.extraction.store import ExamRulesStore

EXPECTED_RELAXATIONS = {"scheduled caste": 5, "other backward": 3, "benchmark disabilities": 10}


@pytest.fixture(scope="module")
def ibps_rules():
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if "CRP-PO" in d["title"])
    rules = ExamRulesStore(settings.exams_path).get(doc["sha256"])
    if rules is None:
        pytest.skip("run scripts.extract_one first")
    return rules


def test_age_window_matches_notification(ibps_rules):
    assert ibps_rules.age is not None
    assert ibps_rules.age.minimum_years == 20
    assert ibps_rules.age.maximum_years == 30


def test_age_reckoned_on_first_july(ibps_rules):
    assert ibps_rules.age.reckoned_on is not None
    assert (ibps_rules.age.reckoned_on.month, ibps_rules.age.reckoned_on.day) == (7, 1)


def test_relaxations_match_official_table(ibps_rules):
    found = {r.category.lower(): r.extra_years for r in ibps_rules.age_relaxations}
    for needle, years in EXPECTED_RELAXATIONS.items():
        matches = [v for k, v in found.items() if needle in k]
        assert matches, f"missing relaxation for {needle}"
        assert matches[0] == years


def test_every_claim_carries_a_citation(ibps_rules):
    for citation in ibps_rules.all_citations():
        assert citation.page > 0
        assert len(citation.quote.strip()) > 15


def test_fee_concession_exists_for_reserved_categories(ibps_rules):
    amounts = sorted(f.amount_rupees for f in ibps_rules.fees)
    assert len(amounts) >= 2
    assert amounts[0] < amounts[-1]
