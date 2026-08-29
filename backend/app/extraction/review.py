from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Literal

from pydantic import BaseModel, Field

from app.extraction.document import Page
from app.extraction.schema import Citation, ExamRules

Severity = Literal["wrong", "unsupported", "missing"]


class ClaimProblem(BaseModel):
    field: str = Field(description="which value is wrong, for example age.maximum_years")
    problem: str = Field(description="what is wrong with it, in one plain sentence")
    severity: Severity


class ReviewResult(BaseModel):
    problems: list[ClaimProblem] = []


@dataclass(frozen=True)
class CitationCheck:
    field: str
    page: int
    found: bool
    match_ratio: float
    quote: str

    @property
    def is_sound(self) -> bool:
        return self.found and self.match_ratio >= 0.85


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def _best_ratio(needle: str, haystack: str) -> float:
    if not needle:
        return 0.0
    if needle in haystack:
        return 1.0
    window = len(needle)
    best = 0.0
    for start in range(0, max(1, len(haystack) - window), max(1, window // 3)):
        chunk = haystack[start : start + window]
        best = max(best, SequenceMatcher(None, needle, chunk).ratio())
        if best >= 0.95:
            break
    return best


def _labelled_citations(rules: ExamRules) -> list[tuple[str, Citation]]:
    pairs: list[tuple[str, Citation]] = []
    if rules.age:
        pairs.append(("age", rules.age.citation))
    for item in rules.age_relaxations:
        pairs.append((f"relaxation[{item.category[:24]}]", item.citation))
    for item in rules.qualifications:
        pairs.append((f"qualification[{item.requirement[:24]}]", item.citation))
    for item in rules.fees:
        pairs.append((f"fee[{item.amount_rupees:.0f}]", item.citation))
    for item in rules.key_dates:
        pairs.append((f"date[{item.label[:24]}]", item.citation))
    return pairs


def check_citations(rules: ExamRules, pages: list[Page]) -> list[CitationCheck]:
    by_number = {p.number: _normalise(p.text) for p in pages}
    checks: list[CitationCheck] = []
    for field, citation in _labelled_citations(rules):
        page_text = by_number.get(citation.page, "")
        ratio = _best_ratio(_normalise(citation.quote), page_text)
        checks.append(
            CitationCheck(
                field=field,
                page=citation.page,
                found=bool(page_text),
                match_ratio=round(ratio, 3),
                quote=citation.quote,
            )
        )
    return checks


def unsound_checks(checks: list[CitationCheck]) -> list[CitationCheck]:
    return [c for c in checks if not c.is_sound]


@dataclass(frozen=True)
class ValueCheck:
    field: str
    value: float
    supported: bool
    numbers_in_quote: tuple[float, ...]
    quote: str


def numbers_in(text: str) -> tuple[float, ...]:
    raw = re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
    return tuple(float(n) for n in raw)


def _numeric_claims(rules: ExamRules) -> list[tuple[str, float, str]]:
    claims: list[tuple[str, float, str]] = []
    if rules.age:
        quote = rules.age.citation.quote
        if rules.age.minimum_years is not None:
            claims.append(("age.minimum_years", float(rules.age.minimum_years), quote))
        if rules.age.maximum_years is not None:
            claims.append(("age.maximum_years", float(rules.age.maximum_years), quote))
    for item in rules.age_relaxations:
        claims.append(
            (f"relaxation[{item.category[:24]}]", float(item.extra_years), item.citation.quote)
        )
    for item in rules.fees:
        claims.append((f"fee[{item.applies_to[:20]}]", item.amount_rupees, item.citation.quote))
    return claims


def check_values(rules: ExamRules) -> list[ValueCheck]:
    checks: list[ValueCheck] = []
    for field, value, quote in _numeric_claims(rules):
        found = numbers_in(quote)
        checks.append(
            ValueCheck(
                field=field,
                value=value,
                supported=value in found,
                numbers_in_quote=found,
                quote=quote,
            )
        )
    return checks


def unsupported_values(checks: list[ValueCheck]) -> list[ValueCheck]:
    return [c for c in checks if not c.supported]


def prune_unsupported(rules: ExamRules, verdict_fields: set[str]) -> ExamRules:
    pruned = rules.model_copy(deep=True)
    dropped: list[str] = []

    if pruned.age and "age.maximum_years" in verdict_fields:
        pruned.age.maximum_years = None
        dropped.append("age.maximum_years")
    if pruned.age and "age.minimum_years" in verdict_fields:
        pruned.age.minimum_years = None
        dropped.append("age.minimum_years")

    kept_relaxations = []
    for item in pruned.age_relaxations:
        label = f"relaxation[{item.category[:24]}]"
        if label in verdict_fields:
            dropped.append(f"age relaxation for {item.category[:40]}")
        else:
            kept_relaxations.append(item)
    pruned.age_relaxations = kept_relaxations

    kept_fees = []
    for item in pruned.fees:
        label = f"fee[{item.applies_to[:20]}]"
        if label in verdict_fields:
            dropped.append(f"application fee for {item.applies_to[:40]}")
        else:
            kept_fees.append(item)
    pruned.fees = kept_fees

    pruned.could_not_verify = dropped
    return pruned
