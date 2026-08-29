from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from app.core.config import get_settings
from app.documents.spec import DocumentKind

PRIVATE_KINDS = {DocumentKind.SIGNATURE, DocumentKind.THUMB_IMPRESSION}


class StoredDocument(BaseModel):
    kind: DocumentKind
    file_id: str
    url: str
    is_private: bool
    size_bytes: int
    stored_at: datetime


class DocumentStore(Protocol):
    def save(self, student_id: int, kind: DocumentKind, payload: bytes) -> StoredDocument: ...


def _file_name(student_id: int, kind: DocumentKind, payload: bytes) -> str:
    digest = hashlib.sha256(payload).hexdigest()[:12]
    return f"student{student_id}_{kind.value}_{digest}.jpg"


class LocalDocumentStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, student_id: int, kind: DocumentKind, payload: bytes) -> StoredDocument:
        name = _file_name(student_id, kind, payload)
        target = self.root / name
        target.write_bytes(payload)
        return StoredDocument(
            kind=kind,
            file_id=name,
            url=f"data:image/jpeg;base64,{base64.b64encode(payload).decode()}",
            is_private=kind in PRIVATE_KINDS,
            size_bytes=len(payload),
            stored_at=datetime.now(timezone.utc),
        )


class ImageKitDocumentStore:
    def __init__(self, private_key: str, url_endpoint: str, folder: str = "/sarathi") -> None:
        from imagekitio import ImageKit

        self.client = ImageKit(private_key=private_key)
        self.url_endpoint = url_endpoint.rstrip("/")
        self.folder = folder

    def save(self, student_id: int, kind: DocumentKind, payload: bytes) -> StoredDocument:
        is_private = kind in PRIVATE_KINDS
        name = _file_name(student_id, kind, payload)

        result = self.client.files.upload(
            file=base64.b64encode(payload).decode(),
            file_name=name,
            folder=f"{self.folder}/student{student_id}",
            is_private_file=is_private,
            use_unique_file_name=False,
        )
        return StoredDocument(
            kind=kind,
            file_id=getattr(result, "file_id", name),
            url=getattr(result, "url", f"{self.url_endpoint}{self.folder}/{name}"),
            is_private=is_private,
            size_bytes=len(payload),
            stored_at=datetime.now(timezone.utc),
        )


def get_document_store() -> DocumentStore:
    settings = get_settings()
    if settings.imagekit_private_key and settings.imagekit_url_endpoint:
        return ImageKitDocumentStore(
            private_key=settings.imagekit_private_key,
            url_endpoint=settings.imagekit_url_endpoint,
        )
    return LocalDocumentStore(settings.notifications_path.parent / "documents")
