from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field
from strands import Agent

from agents.models import fast_model, patient_retries
from agents.prompts import CLASSIFIER_SYSTEM
from agents.resilience import with_retry
from app.extraction.document import Page

DocumentKind = Literal["recruitment_notification", "other"]


class DocumentVerdict(BaseModel):
    kind: DocumentKind
    reason: str = Field(description="one short sentence saying why")


def classify(pages: list[Page], title: str) -> DocumentVerdict:
    if not pages:
        return DocumentVerdict(kind="other", reason="the document has no readable text")

    opening = " ".join(p.text for p in pages[:2])[:2200]
    agent = Agent(
        model=fast_model(),
        system_prompt=CLASSIFIER_SYSTEM,
        callback_handler=None,
        retry_strategy=patient_retries(),
        name="classifier",
        description="decides whether a pdf is a recruitment notification",
    )
    prompt = f"title: {title}\n\nfirst pages:\n{opening}"
    return with_retry(lambda: agent.structured_output(DocumentVerdict, prompt))
