from __future__ import annotations

from pydantic import BaseModel
from strands import Agent

from agents.models import patient_retries, smart_model
from agents.prompts import SPEC_EXTRACTOR_SYSTEM
from agents.resilience import with_retry
from app.documents.spec import DocumentKind, DocumentSpec
from app.extraction import document
from app.extraction.document import Page


class SingleSpec(BaseModel):
    width_px: int | None = None
    height_px: int | None = None
    min_kb: float | None = None
    max_kb: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None
    page: int
    quote: str


TARGETS: dict[DocumentKind, tuple[str, ...]] = {
    DocumentKind.PHOTOGRAPH: document.PHOTO_PATTERNS,
    DocumentKind.SIGNATURE: document.SIGNATURE_PATTERNS,
    DocumentKind.THUMB_IMPRESSION: document.THUMB_PATTERNS,
}

ASKS: dict[DocumentKind, str] = {
    DocumentKind.PHOTOGRAPH: "the photograph",
    DocumentKind.SIGNATURE: "the signature",
    DocumentKind.THUMB_IMPRESSION: "the left thumb impression",
}


def _agent() -> Agent:
    return Agent(
        model=smart_model(),
        system_prompt=SPEC_EXTRACTOR_SYSTEM,
        callback_handler=None,
        retry_strategy=patient_retries(),
        name="spec_extractor",
        description="reads the photo and signature size rules from a notification",
    )


def extract_specs(pages: list[Page]) -> list[DocumentSpec]:
    from app.extraction.schema import Citation

    found: list[DocumentSpec] = []
    for kind, patterns in TARGETS.items():
        snippets = document.snippets_for(pages, patterns, window=800, max_snippets=2)
        if not snippets:
            continue
        prompt = (
            f"{document.render(snippets, char_budget=3200)}\n\n"
            f"Record the required pixel size and file size in KB for {ASKS[kind]}."
        )
        try:
            single = with_retry(lambda: _agent().structured_output(SingleSpec, prompt))
        except Exception:
            continue
        if single.width_px is None and single.max_kb is None:
            continue
        found.append(
            DocumentSpec(
                kind=kind,
                width_px=single.width_px,
                height_px=single.height_px,
                min_kb=single.min_kb,
                max_kb=single.max_kb,
                width_cm=single.width_cm,
                height_cm=single.height_cm,
                citation=Citation(page=single.page, quote=single.quote),
            )
        )
    return found
