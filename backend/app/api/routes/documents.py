from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.current_user import current_user
from app.db.models import User
from app.documents.maker import CannotMeetSpec, make_document
from app.documents.storage import StoredDocument, get_document_store
from app.documents.spec import IBPS_PO_SPECS, KIND_LABEL, DocumentKind, DocumentSpec

router = APIRouter(prefix="/documents", tags=["documents"])


class MadeDocumentOut(BaseModel):
    kind: DocumentKind
    label: str
    width_px: int
    height_px: int
    size_kb: float
    padded: bool
    matches_spec: bool
    needed: str
    image_base64: str


class SpecOut(BaseModel):
    kind: DocumentKind
    label: str
    width_px: int | None
    height_px: int | None
    min_kb: float | None
    max_kb: float | None
    needed: str


@router.get("/specs", response_model=list[SpecOut])
def read_specs() -> list[SpecOut]:
    return [
        SpecOut(
            kind=spec.kind,
            label=KIND_LABEL[spec.kind],
            width_px=spec.width_px,
            height_px=spec.height_px,
            min_kb=spec.min_kb,
            max_kb=spec.max_kb,
            needed=spec.describe(),
        )
        for spec in IBPS_PO_SPECS
    ]


@router.post("/make", response_model=MadeDocumentOut)
async def make(
    file: UploadFile = File(...),
    kind: DocumentKind = Form(...),
    width_px: int = Form(...),
    height_px: int = Form(...),
    min_kb: float | None = Form(default=None),
    max_kb: float | None = Form(default=None),
) -> MadeDocumentOut:
    spec = DocumentSpec(
        kind=kind, width_px=width_px, height_px=height_px, min_kb=min_kb, max_kb=max_kb
    )
    payload = await file.read()
    try:
        made = make_document(payload, spec)
    except CannotMeetSpec as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail="that file is not a readable image") from error

    return MadeDocumentOut(
        kind=kind,
        label=KIND_LABEL[kind],
        width_px=made.width_px,
        height_px=made.height_px,
        size_kb=made.size_kb,
        padded=made.padded,
        matches_spec=made.matches(spec),
        needed=spec.describe(),
        image_base64=base64.b64encode(made.payload).decode(),
    )


class SavedDocumentOut(BaseModel):
    kind: DocumentKind
    label: str
    width_px: int
    height_px: int
    size_kb: float
    matches_spec: bool
    is_private: bool
    file_id: str
    view_url: str
    stored_where: str


@router.post("/save", response_model=SavedDocumentOut, status_code=201)
async def save(
    file: UploadFile = File(...),
    kind: DocumentKind = Form(...),
    width_px: int = Form(...),
    height_px: int = Form(...),
    min_kb: float | None = Form(default=None),
    max_kb: float | None = Form(default=None),
    user: User = Depends(current_user),
) -> SavedDocumentOut:
    spec = DocumentSpec(
        kind=kind, width_px=width_px, height_px=height_px, min_kb=min_kb, max_kb=max_kb
    )
    payload = await file.read()
    try:
        made = make_document(payload, spec)
    except CannotMeetSpec as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail="that file is not a readable image") from error

    store = get_document_store()
    stored: StoredDocument = store.save(
        student_id=user.student_id or user.id, kind=kind, payload=made.payload
    )

    return SavedDocumentOut(
        kind=kind,
        label=KIND_LABEL[kind],
        width_px=made.width_px,
        height_px=made.height_px,
        size_kb=made.size_kb,
        matches_spec=made.matches(spec),
        is_private=stored.is_private,
        file_id=stored.file_id,
        view_url=stored.view_url or stored.url,
        stored_where=type(store).__name__.replace("DocumentStore", ""),
    )
