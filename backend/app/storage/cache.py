from __future__ import annotations

import hashlib
import io
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

from app.core.http import build_client
from app.storage.documents import CachedDocument, CacheIndex

INDEX_FILENAME = "index.json"
PDF_MAGIC = b"%PDF-"


class NotCachedError(RuntimeError):
    pass


class NotificationCache:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / INDEX_FILENAME
        self.index = self._load_index()

    def _load_index(self) -> CacheIndex:
        if self.index_path.exists():
            return CacheIndex.model_validate_json(self.index_path.read_text("utf-8"))
        return CacheIndex()

    def _save_index(self) -> None:
        self.index_path.write_text(
            self.index.model_dump_json(indent=2), encoding="utf-8"
        )

    def get(self, origin_url: str) -> CachedDocument | None:
        return self.index.by_origin().get(origin_url)

    def read_bytes(self, document: CachedDocument) -> bytes:
        path = document.path_under(self.root)
        if not path.exists():
            raise NotCachedError(f"file missing for {document.origin_url}")
        return path.read_bytes()

    def store(self, source_id: str, title: str, origin_url: str, referer: str) -> CachedDocument:
        existing = self.get(origin_url)
        if existing:
            return existing

        with build_client(referer=referer) as client:
            response = client.get(origin_url)
            response.raise_for_status()
            payload = response.content

        return self.store_bytes(source_id, title, origin_url, payload)

    def store_bytes(
        self, source_id: str, title: str, origin_url: str, payload: bytes
    ) -> CachedDocument:
        existing = self.get(origin_url)
        if existing:
            return existing

        if not payload.startswith(PDF_MAGIC):
            raise ValueError(f"not a pdf: {origin_url}")

        digest = hashlib.sha256(payload).hexdigest()
        already = self.index.by_hash().get(digest)
        if already:
            return already

        relative_path = f"{source_id}/{digest[:16]}.pdf"
        destination = self.root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)

        document = CachedDocument(
            source_id=source_id,
            title=title,
            origin_url=origin_url,
            sha256=digest,
            byte_size=len(payload),
            page_count=_count_pages(payload),
            fetched_at=datetime.now(timezone.utc),
            relative_path=relative_path,
        )
        self.index.documents.append(document)
        self._save_index()
        return document


def _count_pages(payload: bytes) -> int | None:
    try:
        return len(PdfReader(io.BytesIO(payload)).pages)
    except Exception:
        return None
