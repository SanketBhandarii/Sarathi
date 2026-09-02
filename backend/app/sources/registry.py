from __future__ import annotations

from types import ModuleType

from app.sources import ibps, india_post, ssc, upsc
from app.sources.base import Notice

SOURCES: tuple[ModuleType, ...] = (ssc, upsc, ibps, india_post)


def get_source(source_id: str) -> ModuleType:
    for source in SOURCES:
        if source.id == source_id:
            return source
    raise KeyError(f"unknown source: {source_id}")


def fetch_all() -> dict[str, list[Notice]]:
    return {source.id: source.fetch_notices() for source in SOURCES}
