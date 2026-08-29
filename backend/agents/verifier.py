from __future__ import annotations

from dataclasses import dataclass

from strands import Agent

from agents.models import smart_model
from agents.prompts import VERIFIER_SYSTEM
from agents.resilience import with_retry
from app.extraction.document import Page
from app.extraction.review import (
    CitationCheck,
    ClaimProblem,
    ReviewResult,
    ValueCheck,
    check_citations,
    check_values,
    unsound_checks,
    unsupported_values,
)
from app.extraction.schema import ExamRules
from tools.document_tools import find_text_in_document, quote_appears_on_page, read_page


@dataclass(frozen=True)
class Verdict:
    citation_checks: list[CitationCheck]
    value_checks: list[ValueCheck]
    problems: list[ClaimProblem]

    @property
    def is_clean(self) -> bool:
        return not self.problems

    def summary(self) -> str:
        return (
            f"{len(self.citation_checks)} quotes checked, "
            f"{len(self.value_checks)} numbers checked, "
            f"{len(self.problems)} problems"
        )


def build_verifier() -> Agent:
    return Agent(
        model=smart_model(),
        system_prompt=VERIFIER_SYSTEM,
        tools=[quote_appears_on_page, read_page, find_text_in_document],
        callback_handler=None,
        name="verifier",
        description="re-reads the notification and tries to prove the extractor wrong",
    )


def _describe(rules: ExamRules) -> str:
    lines = [f"document_sha256: {rules.document_sha256}", f"exam: {rules.exam_name}", ""]
    if rules.age:
        a = rules.age
        lines.append(
            f"age: minimum {a.minimum_years}, maximum {a.maximum_years}, as on {a.reckoned_on}"
            f' | page {a.citation.page} | "{a.citation.quote[:150]}"'
        )
    for r in rules.age_relaxations:
        lines.append(
            f"relaxation: {r.category} = +{r.extra_years} years"
            f' | page {r.citation.page} | "{r.citation.quote[:110]}"'
        )
    for q in rules.qualifications:
        lines.append(f"qualification: {q.requirement} | page {q.citation.page}")
    for f in rules.fees:
        lines.append(f"fee: Rs {f.amount_rupees:.0f} for {f.applies_to} | page {f.citation.page}")
    return "\n".join(lines)


def _mechanical_problems(
    citation_checks: list[CitationCheck], value_checks: list[ValueCheck]
) -> list[ClaimProblem]:
    problems = [
        ClaimProblem(
            field=check.field,
            problem=(
                f"the quoted sentence is not on page {check.page} "
                f"(best match only {check.match_ratio:.0%})"
            ),
            severity="unsupported",
        )
        for check in unsound_checks(citation_checks)
    ]
    problems.extend(
        ClaimProblem(
            field=check.field,
            problem=(
                f"recorded as {check.value:g} but that number does not appear in the "
                f"quoted sentence"
            ),
            severity="wrong",
        )
        for check in unsupported_values(value_checks)
    )
    return problems


def verify(rules: ExamRules, pages: list[Page], use_model: bool = True) -> Verdict:
    citation_checks = check_citations(rules, pages)
    value_checks = check_values(rules)
    problems = _mechanical_problems(citation_checks, value_checks)

    if use_model:
        prompt = (
            f"{_describe(rules)}\n\n"
            "For each claim above, compare the recorded value against the sentence quoted "
            "beside it. If that sentence does not contain the exact number, date or category "
            "recorded, the claim is wrong. Use your tools to read the page and confirm. "
            "Assume nothing is correct until you have checked it against the page."
        )
        reviewed: ReviewResult = with_retry(
            lambda: build_verifier().structured_output(ReviewResult, prompt)
        )
        known = {p.field for p in problems}
        problems.extend(p for p in reviewed.problems if p.field not in known)

    return Verdict(citation_checks, value_checks, problems)
