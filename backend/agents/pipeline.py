from __future__ import annotations

from dataclasses import dataclass, field

from agents import extractor
from agents.prompts import CORRECTION_HINT
from agents.verifier import Verdict, verify
from app.extraction.document import Page, has_readable_text
from app.extraction.review import prune_unsupported
from app.extraction.schema import ExamRules
from app.extraction.windows import find_last_date_to_apply


@dataclass
class PipelineResult:
    rules: ExamRules
    verdict: Verdict
    attempts: int
    history: list[str] = field(default_factory=list)

    @property
    def trustworthy(self) -> bool:
        return self.verdict.is_clean


def _problem_list(verdict: Verdict) -> str:
    return "\n".join(f"- {p.field}: {p.problem}" for p in verdict.problems)


def extract_and_verify(
    pages: list[Page],
    exam_name: str,
    source_id: str,
    sha256: str,
    max_attempts: int = 3,
    use_model_review: bool = True,
) -> PipelineResult:
    history: list[str] = []

    if not has_readable_text(pages):
        empty = ExamRules(
            exam_name=exam_name,
            source_id=source_id,
            document_sha256=sha256,
            could_not_verify=["this notification is a scanned image, we cannot read its text"],
        )
        return PipelineResult(
            rules=empty,
            verdict=verify(empty, pages, use_model=False),
            attempts=0,
            history=["skipped: scanned document with no readable text"],
        )

    rules = extractor.extract_rules(pages, exam_name, source_id, sha256)
    verdict = verify(rules, pages, use_model=use_model_review)
    history.append(f"attempt 1: {verdict.summary()}")

    attempt = 1
    while not verdict.is_clean and attempt < max_attempts:
        attempt += 1
        hint = CORRECTION_HINT.format(problems=_problem_list(verdict))
        age = extractor.extract_age(pages, extra_instruction=hint)
        rules = rules.model_copy(
            update={"age": age.age, "age_relaxations": age.relaxations}
        )
        verdict = verify(rules, pages, use_model=use_model_review)
        history.append(f"attempt {attempt}: {verdict.summary()}")

    if not verdict.is_clean:
        rules = prune_unsupported(rules, {p.field for p in verdict.problems})
        verdict = verify(rules, pages, use_model=False)
        history.append(f"pruned unverifiable claims: {verdict.summary()}")

    rules, note = _add_last_date_if_missing(rules, pages)
    if note:
        history.append(note)

    return PipelineResult(rules=rules, verdict=verdict, attempts=attempt, history=history)


def _already_knows_when_it_closes(rules: ExamRules) -> bool:
    return any(
        "last" in entry.label.lower() or "clos" in entry.label.lower()
        for entry in rules.key_dates
    )


def _add_last_date_if_missing(rules: ExamRules, pages: list[Page]) -> tuple[ExamRules, str | None]:
    if _already_knows_when_it_closes(rules):
        return rules, None

    found = find_last_date_to_apply([page.text for page in pages])
    if found is None:
        return rules, "no last date to apply anywhere in this document, so it stays unknown"

    return (
        rules.model_copy(update={"key_dates": [*rules.key_dates, found]}),
        f"read the last date to apply from page {found.citation.page}: {found.happens_on}",
    )
