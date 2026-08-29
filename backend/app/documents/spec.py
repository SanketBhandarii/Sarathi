from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.extraction.schema import Citation


class DocumentKind(StrEnum):
    PHOTOGRAPH = "photograph"
    SIGNATURE = "signature"
    THUMB_IMPRESSION = "thumb_impression"


KIND_LABEL: dict[DocumentKind, str] = {
    DocumentKind.PHOTOGRAPH: "Photo",
    DocumentKind.SIGNATURE: "Signature",
    DocumentKind.THUMB_IMPRESSION: "Thumb impression",
}


class DocumentSpec(BaseModel):
    kind: DocumentKind
    width_px: int | None = None
    height_px: int | None = None
    min_kb: float | None = None
    max_kb: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None
    file_format: str = "JPEG"
    citation: Citation | None = None

    def describe(self) -> str:
        parts: list[str] = []
        if self.width_px and self.height_px:
            parts.append(f"{self.width_px} x {self.height_px} pixels")
        if self.width_cm and self.height_cm:
            parts.append(f"{self.width_cm:g} x {self.height_cm:g} cm")
        if self.min_kb is not None and self.max_kb is not None:
            parts.append(f"{self.min_kb:g} to {self.max_kb:g} KB")
        elif self.max_kb is not None:
            parts.append(f"under {self.max_kb:g} KB")
        return ", ".join(parts) or "no size given"


IBPS_PO_SPECS: list[DocumentSpec] = [
    DocumentSpec(
        kind=DocumentKind.PHOTOGRAPH,
        width_px=200, height_px=230, min_kb=20, max_kb=50,
        width_cm=3.5, height_cm=4.5,
    ),
    DocumentSpec(
        kind=DocumentKind.SIGNATURE,
        width_px=140, height_px=60, min_kb=10, max_kb=20,
    ),
    DocumentSpec(
        kind=DocumentKind.THUMB_IMPRESSION,
        width_px=240, height_px=240, min_kb=20, max_kb=50,
        width_cm=3.0, height_cm=3.0,
    ),
]
