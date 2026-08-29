from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


class Notice(BaseModel):
    source_id: str
    title: str
    detail_url: str
    document_url: str | None = None
    opens_on: date | None = None
    closes_on: date | None = None
    year: str | None = None

    @field_validator("title")
    @classmethod
    def _collapse_whitespace(cls, value: str) -> str:
        return " ".join(value.split())


@runtime_checkable
class Source(Protocol):
    id: str
    name: str
    home_url: str
    official_domains: tuple[str, ...]

    def fetch_notices(self) -> list[Notice]: ...


def is_official_url(url: str, official_domains: tuple[str, ...]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in official_domains)
