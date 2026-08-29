from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from app.sources.ssc_calendar import CalendarEntry


class CalendarFile(BaseModel):
    entries: list[CalendarEntry] = []


class CalendarStore:
    def __init__(self, root: Path) -> None:
        self.root = root / "calendar"
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "ssc_calendar.json"

    def get(self) -> list[CalendarEntry]:
        if not self.path.exists():
            return []
        return CalendarFile.model_validate_json(self.path.read_text("utf-8")).entries

    def put(self, entries: list[CalendarEntry]) -> None:
        self.path.write_text(
            CalendarFile(entries=entries).model_dump_json(indent=2), encoding="utf-8"
        )
