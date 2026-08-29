from __future__ import annotations

import json

import pytest

from app.core.config import get_settings
from app.extraction.document import load_pages
from app.extraction.review import check_citations, unsound_checks
from app.extraction.schema import Citation
from app.extraction.store import ExamRulesStore


@pytest.fixture(scope="module")
def rules_and_pages():
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if "CRP-PO" in d["title"])
    rules = ExamRulesStore(settings.exams_path).get(doc["sha256"])
    if rules is None:
        pytest.skip("run scripts.extract_one first")
    pages = load_pages(settings.notifications_path / doc["relative_path"])
    return rules, pages


def test_real_citations_all_pass(rules_and_pages):
    rules, pages = rules_and_pages
    assert unsound_checks(check_citations(rules, pages)) == []


def test_invented_quote_is_caught(rules_and_pages):
    rules, pages = rules_and_pages
    tampered = rules.model_copy(deep=True)
    tampered.age.citation = Citation(
        page=6, quote="The maximum age limit for all candidates is 45 years."
    )
    bad = unsound_checks(check_citations(tampered, pages))
    assert any(c.field == "age" for c in bad)


def test_right_quote_on_wrong_page_is_caught(rules_and_pages):
    rules, pages = rules_and_pages
    tampered = rules.model_copy(deep=True)
    tampered.age.citation = Citation(page=40, quote=rules.age.citation.quote)
    bad = unsound_checks(check_citations(tampered, pages))
    assert any(c.field == "age" for c in bad)


def test_subtly_altered_number_is_caught(rules_and_pages):
    rules, pages = rules_and_pages
    tampered = rules.model_copy(deep=True)
    original = rules.age.citation.quote
    tampered.age.citation = Citation(page=6, quote=original.replace("20 years", "26 years"))
    checks = check_citations(tampered, pages)
    age_check = next(c for c in checks if c.field == "age")
    assert age_check.match_ratio < 1.0
