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


SIGNED_URL_SECONDS = 3600


class StoredDocument(BaseModel):
    kind: DocumentKind
    file_id: str
    url: str
    view_url: str | None = None
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
        data_url = f"data:image/jpeg;base64,{base64.b64encode(payload).decode()}"
        return StoredDocument(
            kind=kind,
            file_id=name,
            url=data_url,
            view_url=data_url,
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
            file=payload,
            file_name=name,
            folder=f"{self.folder}/student{student_id}",
            is_private_file=is_private,
            overwrite_file=True,
        )
        url = getattr(result, "url", f"{self.url_endpoint}{self.folder}/{name}")
        return StoredDocument(
            kind=kind,
            file_id=getattr(result, "file_id", name),
            url=url,
            view_url=self.viewable_url(url) if is_private else url,
            is_private=is_private,
            size_bytes=len(payload),
            stored_at=datetime.now(timezone.utc),
        )

    def viewable_url(self, url: str, seconds: int = SIGNED_URL_SECONDS) -> str:
        return self.client.helper.build_url(
            src=url, url_endpoint=self.url_endpoint, signed=True, expires_in=seconds
        )


def master_path(student_id: int, kind: DocumentKind) -> Path:
    from app.core.config import get_settings

    root = get_settings().notifications_path.parent / "masters" / f"student{student_id}"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{kind.value}.bin"


def keep_master(student_id: int, kind: DocumentKind, payload: bytes) -> None:
    master_path(student_id, kind).write_bytes(payload)


def read_master(student_id: int, kind: DocumentKind) -> bytes | None:
    path = master_path(student_id, kind)
    return path.read_bytes() if path.exists() else None


def get_document_store() -> DocumentStore:
    settings = get_settings()
    if settings.imagekit_private_key and settings.imagekit_url_endpoint:
        return ImageKitDocumentStore(
            private_key=settings.imagekit_private_key,
            url_endpoint=settings.imagekit_url_endpoint,
            folder=settings.imagekit_folder,
        )
    return LocalDocumentStore(settings.notifications_path.parent / "documents")
