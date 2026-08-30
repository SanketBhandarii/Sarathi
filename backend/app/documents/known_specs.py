from __future__ import annotations

from pydantic import BaseModel

from app.documents.spec import DocumentKind, DocumentSpec


class BodyRules(BaseModel):
    source_id: str
    body: str
    specs: list[DocumentSpec]
    warnings: list[str] = []
    checked_against: str


SSC = BodyRules(
    source_id="ssc",
    body="Staff Selection Commission",
    specs=[
        DocumentSpec(
            kind=DocumentKind.PHOTOGRAPH,
            width_px=275, height_px=354, width_cm=3.5, height_cm=4.5,
            min_kb=20, max_kb=50,
        ),
        DocumentSpec(
            kind=DocumentKind.SIGNATURE,
            width_px=236, height_px=79, width_cm=4.0, height_cm=2.0,
            min_kb=10, max_kb=20,
        ),
    ],
    warnings=[
        "From 2026 SSC will not accept a photo from your gallery. You must take it live "
        "on the camera in their own portal or the mySSC app.",
        "No spectacles, no cap and no mask, even if you wear glasses every day.",
        "Sign in black ink on white paper. Not in capital letters.",
    ],
    checked_against="ssc.gov.in one time registration rules",
)

IBPS = BodyRules(
    source_id="ibps",
    body="Institute of Banking Personnel Selection",
    specs=[
        DocumentSpec(
            kind=DocumentKind.PHOTOGRAPH,
            width_px=200, height_px=230, width_cm=3.5, height_cm=4.5,
            min_kb=20, max_kb=50,
        ),
        DocumentSpec(
            kind=DocumentKind.SIGNATURE, width_px=140, height_px=60, min_kb=10, max_kb=20
        ),
        DocumentSpec(
            kind=DocumentKind.THUMB_IMPRESSION,
            width_px=240, height_px=240, width_cm=3.0, height_cm=3.0,
            min_kb=20, max_kb=50,
        ),
    ],
    warnings=[
        "A recent passport style colour photo against a light background.",
        "You also need a left thumb impression in black or blue ink on white paper.",
    ],
    checked_against="ibps CRP PO notification, annexure III",
)

UPSC = BodyRules(
    source_id="upsc",
    body="Union Public Service Commission",
    specs=[
        DocumentSpec(
            kind=DocumentKind.PHOTOGRAPH,
            width_px=350, height_px=450, width_cm=3.5, height_cm=4.5,
            min_kb=20, max_kb=200,
        ),
        DocumentSpec(
            kind=DocumentKind.SIGNATURE, width_px=350, height_px=150, min_kb=20, max_kb=100
        ),
    ],
    warnings=[
        "UPSC wants your signature three times, one below the other on white paper, "
        "scanned as a single picture.",
        "Your face should fill about three quarters of the photograph.",
    ],
    checked_against="upsc online application guidelines",
)

MPSC = BodyRules(
    source_id="mpsc",
    body="Maharashtra Public Service Commission",
    specs=[
        DocumentSpec(
            kind=DocumentKind.PHOTOGRAPH,
            width_px=200, height_px=230, width_cm=3.5, height_cm=4.5,
            min_kb=20, max_kb=50,
        ),
        DocumentSpec(
            kind=DocumentKind.SIGNATURE, width_px=140, height_px=60, min_kb=10, max_kb=20
        ),
    ],
    warnings=[
        "MPSC publishes its notifications as scanned pictures, so check the sizes in "
        "the notification itself before you upload."
    ],
    checked_against="commonly asked sizes, not read from a notification",
)

BY_SOURCE: dict[str, BodyRules] = {
    rules.source_id: rules for rules in (SSC, IBPS, UPSC, MPSC)
}


def rules_for(source_id: str) -> BodyRules | None:
    return BY_SOURCE.get(source_id)


def every_body() -> list[BodyRules]:
    return [SSC, IBPS, UPSC, MPSC]
