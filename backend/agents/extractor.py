from __future__ import annotations

from strands import Agent

from agents.models import patient_retries, smart_model
from agents.prompts import EXTRACTOR_SYSTEM
from agents.resilience import with_retry
from app.extraction import document
from app.extraction.document import Page, Snippet
from app.extraction.schema import (
    AgeSection,
    DateSection,
    ExamRules,
    FeeSection,
    QualificationSection,
)


def _agent() -> Agent:
    return Agent(
        model=smart_model(),
        system_prompt=EXTRACTOR_SYSTEM,
        callback_handler=None,
        retry_strategy=patient_retries(),
        name="extractor",
        description="reads one section of a notification and records it with citations",
    )


def _extract(schema: type, snippets: list[Snippet], instruction: str):
    if not snippets:
        return schema()
    prompt = f"{document.render(snippets)}\n\n{instruction}"
    return with_retry(lambda: _agent().structured_output(schema, prompt))


def extract_age(pages: list[Page], extra_instruction: str = "") -> AgeSection:
    return _extract(
        AgeSection,
        document.snippets_for(pages, document.AGE_PATTERNS),
        "Record the age limits and every age relaxation category shown." + (f"\n\n{extra_instruction}" if extra_instruction else ""),
    )


def extract_qualifications(pages: list[Page]) -> QualificationSection:
    return _extract(
        QualificationSection,
        document.snippets_for(pages, document.QUALIFICATION_PATTERNS),
        "Record the educational qualifications required.",
    )


def extract_fees(pages: list[Page]) -> FeeSection:
    return _extract(
        FeeSection,
        document.snippets_for(pages, document.FEE_PATTERNS),
        "Record the application fee for each type of candidate.",
    )


def extract_dates(pages: list[Page]) -> DateSection:
    return _extract(
        DateSection,
        document.snippets_for(pages, document.DATE_PATTERNS),
        "Record the important dates.",
    )


def extract_rules(pages: list[Page], exam_name: str, source_id: str, sha256: str) -> ExamRules:
    age = extract_age(pages)
    return ExamRules(
        exam_name=exam_name,
        source_id=source_id,
        document_sha256=sha256,
        age=age.age,
        age_relaxations=age.relaxations,
        qualifications=extract_qualifications(pages).qualifications,
        fees=extract_fees(pages).fees,
        key_dates=extract_dates(pages).key_dates,
    )
