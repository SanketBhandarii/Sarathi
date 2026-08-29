from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from strands import tool

from app.core.config import get_settings
from app.extraction import document as doc
from app.extraction.document import Page, load_pages
from app.extraction.review import check_citations, check_values, unsound_checks, unsupported_values
from app.extraction.schema import AgeRelaxation, AgeRule, Citation, ExamRules
from app.extraction.store import ExamRulesStore

SECTIONS = {
    "age": doc.AGE_PATTERNS,
    "qualification": doc.QUALIFICATION_PATTERNS,
    "fee": doc.FEE_PATTERNS,
    "dates": doc.DATE_PATTERNS,
}

_drafts: dict[str, ExamRules] = {}


@lru_cache(maxsize=32)
def _pages(sha256: str) -> tuple[Page, ...]:
    settings = get_settings()
    index = json.loads((settings.notifications_path / "index.json").read_text("utf-8"))
    entry = next(d for d in index["documents"] if d["sha256"] == sha256)
    return tuple(load_pages(settings.notifications_path / entry["relative_path"]))


def draft_for(sha256: str) -> ExamRules | None:
    return _drafts.get(sha256)


def start_draft(sha256: str, exam_name: str, source_id: str) -> None:
    _drafts[sha256] = ExamRules(
        exam_name=exam_name, source_id=source_id, document_sha256=sha256
    )


@tool
def read_section(document_sha256: str, section: str) -> str:
    """Read the part of a notification that talks about age, qualification, fee or dates.

    Valid sections are: age, qualification, fee, dates.
    """
    patterns = SECTIONS.get(section.lower())
    if patterns is None:
        return f"unknown section '{section}'. use one of: {', '.join(SECTIONS)}"
    snippets = doc.snippets_for(list(_pages(document_sha256)), patterns, window=650, max_snippets=2)
    if not snippets:
        return f"this notification has nothing about {section}"
    return doc.render(snippets, char_budget=1800)


@tool
def record_age_rule(
    document_sha256: str,
    minimum_years: int,
    maximum_years: int,
    page: int,
    quote: str,
) -> str:
    """Write down the age limits, with the page and the sentence they came from."""
    draft = _drafts.get(document_sha256)
    if draft is None:
        return "no draft started for this document"
    draft.age = AgeRule(
        minimum_years=minimum_years,
        maximum_years=maximum_years,
        citation=Citation(page=page, quote=quote),
    )
    return f"recorded age {minimum_years} to {maximum_years} from page {page}"


@tool
def record_age_relaxation(
    document_sha256: str, category: str, extra_years: int, page: int, quote: str
) -> str:
    """Write down one age relaxation, with the page and the sentence it came from."""
    draft = _drafts.get(document_sha256)
    if draft is None:
        return "no draft started for this document"
    draft.age_relaxations = [
        r for r in draft.age_relaxations if r.category.lower() != category.lower()
    ]
    draft.age_relaxations.append(
        AgeRelaxation(
            category=category,
            extra_years=extra_years,
            citation=Citation(page=page, quote=quote),
        )
    )
    return f"recorded {category} +{extra_years} years from page {page}"


@tool
def check_what_was_recorded(document_sha256: str) -> str:
    """Check every recorded value against the actual pages of the notification.

    Reports any claim whose quote is not on the page it cites, or whose number
    does not appear in the sentence quoted beside it.
    """
    draft = _drafts.get(document_sha256)
    if draft is None:
        return "no draft started for this document"

    pages = list(_pages(document_sha256))
    bad_quotes = unsound_checks(check_citations(draft, pages))
    bad_values = unsupported_values(check_values(draft))

    if not bad_quotes and not bad_values:
        recorded = 1 if draft.age else 0
        return (
            f"all good. {recorded} age rule and "
            f"{len(draft.age_relaxations)} relaxations checked, no problems found"
        )

    lines = ["problems found:"]
    lines += [
        f"- {c.field}: the quoted sentence is not on page {c.page} "
        f"(best match {c.match_ratio:.0%})"
        for c in bad_quotes
    ]
    lines += [
        f"- {c.field}: recorded as {c.value:g} but that number is not in the quote"
        for c in bad_values
    ]
    return "\n".join(lines)


def save_draft(sha256: str) -> ExamRules | None:
    draft = _drafts.get(sha256)
    if draft is not None:
        ExamRulesStore(get_settings().exams_path).put(draft)
    return draft
