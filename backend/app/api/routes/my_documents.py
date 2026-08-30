from __future__ import annotations

import io
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.current_user import current_user
from app.api.deps import get_db
from app.db.models import StudentDocument, User
from app.documents.spec import KIND_LABEL, DocumentKind
from app.documents.known_specs import every_body
from app.documents.maker import CannotMeetSpec, make_document
from app.documents.storage import get_document_store, keep_master, read_master, viewable_now

router = APIRouter(prefix="/me/documents", tags=["my documents"])

MAX_BYTES = 12 * 1024 * 1024
MIN_SIDE = 120

GUIDANCE: dict[DocumentKind, str] = {
    DocumentKind.PHOTOGRAPH: (
        "A recent passport style photo, taken against a plain light background, "
        "looking straight at the camera. No cap and no dark glasses."
    ),
    DocumentKind.SIGNATURE: (
        "Sign on white paper with a black pen and photograph it. Not in capital letters."
    ),
    DocumentKind.THUMB_IMPRESSION: (
        "Put your left thumb on white paper with black or blue ink and photograph it."
    ),
}


class MasterDocumentOut(BaseModel):
    kind: DocumentKind
    label: str
    guidance: str
    file_id: str | None = None
    view_url: str | None = None
    is_private: bool = False
    width_px: int | None = None
    height_px: int | None = None
    byte_size: int | None = None
    uploaded_at: datetime | None = None

    @property
    def is_uploaded(self) -> bool:
        return self.file_id is not None


def _blank(kind: DocumentKind) -> MasterDocumentOut:
    return MasterDocumentOut(kind=kind, label=KIND_LABEL[kind], guidance=GUIDANCE[kind])


def _to_out(row: StudentDocument) -> MasterDocumentOut:
    kind = DocumentKind(row.kind)
    return MasterDocumentOut(
        kind=kind,
        label=KIND_LABEL[kind],
        guidance=GUIDANCE[kind],
        file_id=row.file_id,
        view_url=viewable_now(row.url, row.is_private),
        is_private=row.is_private,
        width_px=row.width_px,
        height_px=row.height_px,
        byte_size=row.byte_size,
        uploaded_at=row.uploaded_at,
    )


def _student_id(user: User) -> int:
    if not user.student_id:
        raise HTTPException(status_code=409, detail="Please fill your details first.")
    return user.student_id


@router.get("", response_model=list[MasterDocumentOut])
def read_my_documents(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[MasterDocumentOut]:
    student_id = _student_id(user)
    rows = {
        row.kind: row
        for row in db.scalars(
            select(StudentDocument).where(StudentDocument.student_id == student_id)
        ).all()
    }
    return [
        _to_out(rows[kind.value]) if kind.value in rows else _blank(kind)
        for kind in DocumentKind
    ]


@router.post("/{kind}", response_model=MasterDocumentOut, status_code=201)
async def upload_master(
    kind: DocumentKind,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> MasterDocumentOut:
    student_id = _student_id(user)
    payload = await file.read()

    if len(payload) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="That picture is too big. Keep it under 12 MB.")

    try:
        image = Image.open(io.BytesIO(payload))
        image.verify()
        image = Image.open(io.BytesIO(payload))
    except Exception as error:
        raise HTTPException(status_code=400, detail="That file is not a picture.") from error

    if min(image.width, image.height) < MIN_SIDE:
        raise HTTPException(
            status_code=422,
            detail=(
                f"That picture is only {image.width} by {image.height}. "
                "Take a clearer one, at least 120 across."
            ),
        )

    keep_master(student_id, kind, payload)
    stored = get_document_store().save(student_id=student_id, kind=kind, payload=payload)

    row = db.scalar(
        select(StudentDocument).where(
            StudentDocument.student_id == student_id, StudentDocument.kind == kind.value
        )
    )
    if row is None:
        row = StudentDocument(student_id=student_id, kind=kind.value)
        db.add(row)

    row.file_id = stored.file_id
    row.url = stored.url
    row.view_url = stored.view_url or stored.url
    row.is_private = stored.is_private
    row.byte_size = len(payload)
    row.width_px = image.width
    row.height_px = image.height
    db.flush()

    return _to_out(row)


class SizedFileOut(BaseModel):
    source_id: str
    body: str
    needed: str
    width_px: int
    height_px: int
    size_kb: float
    matches: bool
    padded: bool
    image_base64: str


@router.get("/{kind}/sizes", response_model=list[SizedFileOut])
def sizes_for(
    kind: DocumentKind,
    user: User = Depends(current_user),
) -> list[SizedFileOut]:
    import base64

    student_id = _student_id(user)
    master = read_master(student_id, kind)
    if master is None:
        raise HTTPException(
            status_code=404, detail=f"Add your {KIND_LABEL[kind].lower()} first."
        )

    made: list[SizedFileOut] = []
    for rules in every_body():
        spec = next((s for s in rules.specs if s.kind is kind), None)
        if spec is None:
            continue
        try:
            result = make_document(master, spec)
        except CannotMeetSpec:
            continue
        made.append(
            SizedFileOut(
                source_id=rules.source_id,
                body=rules.body,
                needed=spec.describe(),
                width_px=result.width_px,
                height_px=result.height_px,
                size_kb=result.size_kb,
                matches=result.matches(spec),
                padded=result.padded,
                image_base64=base64.b64encode(result.payload).decode(),
            )
        )
    return made
