from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class CachedDocument(BaseModel):
    source_id: str
    title: str
    origin_url: str
    sha256: str
    byte_size: int
    page_count: int | None
    fetched_at: datetime
    relative_path: str

    def path_under(self, root: Path) -> Path:
        return root / self.relative_path


class CacheIndex(BaseModel):
    documents: list[CachedDocument] = []

    def by_hash(self) -> dict[str, CachedDocument]:
        return {d.sha256: d for d in self.documents}

    def by_origin(self) -> dict[str, CachedDocument]:
        return {d.origin_url: d for d in self.documents}
