from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, computed_field


class Level(StrEnum):
    CLASS_10 = "class_10"
    CLASS_12 = "class_12"
    ITI = "iti"
    DIPLOMA = "diploma"
    GRADUATION = "graduation"
    POST_GRADUATION = "post_graduation"


LEVEL_LABEL: dict[Level, str] = {
    Level.CLASS_10: "10th standard",
    Level.CLASS_12: "12th standard",
    Level.ITI: "ITI",
    Level.DIPLOMA: "Diploma",
    Level.GRADUATION: "Graduation",
    Level.POST_GRADUATION: "Post graduation",
}

LEVEL_ORDER: list[Level] = [
    Level.CLASS_10,
    Level.CLASS_12,
    Level.ITI,
    Level.DIPLOMA,
    Level.GRADUATION,
    Level.POST_GRADUATION,
]

RANK = {level: index for index, level in enumerate(LEVEL_ORDER)}


class MarksKind(StrEnum):
    PERCENTAGE = "percentage"
    CGPA = "cgpa"


class Qualification(BaseModel):
    level: Level
    board_or_university: str | None = None
    college: str | None = None
    stream: str | None = None
    marks_kind: MarksKind = MarksKind.PERCENTAGE
    marks: float | None = None
    cgpa_scale: float | None = None
    passed_year: int | None = None
    passed_on: date | None = None
    is_completed: bool = True
    current_semester: int | None = None

    @computed_field
    @property
    def label(self) -> str:
        return LEVEL_LABEL[self.level]

    @computed_field
    @property
    def percentage(self) -> float | None:
        if self.marks is None:
            return None
        if self.marks_kind is MarksKind.PERCENTAGE:
            return round(self.marks, 2)
        scale = self.cgpa_scale or 10.0
        if scale <= 0:
            return None
        return round((self.marks / scale) * 100, 2)

    @computed_field
    @property
    def shown_marks(self) -> str:
        if self.marks is None:
            return "not given"
        if self.marks_kind is MarksKind.PERCENTAGE:
            return f"{self.marks:g}%"
        scale = self.cgpa_scale or 10.0
        return f"{self.marks:g} CGPA out of {scale:g}"

    @computed_field
    @property
    def conversion_note(self) -> str | None:
        if self.marks_kind is not MarksKind.CGPA or self.percentage is None:
            return None
        return (
            f"Forms usually want a percentage. {self.shown_marks} works out to "
            f"about {self.percentage:g}%. Use the conversion your university prints, "
            "not this one, if they differ."
        )


class EducationHistory(BaseModel):
    entries: list[Qualification] = []

    def by_level(self, level: Level) -> Qualification | None:
        return next((entry for entry in self.entries if entry.level is level), None)

    @computed_field
    @property
    def highest_completed(self) -> Level | None:
        finished = [entry.level for entry in self.entries if entry.is_completed]
        return max(finished, key=lambda level: RANK[level]) if finished else None

    def meets(self, level: Level) -> bool:
        highest = self.highest_completed
        return highest is not None and RANK[highest] >= RANK[level]

    def percentage_at(self, level: Level) -> float | None:
        entry = self.by_level(level)
        return entry.percentage if entry else None

    @computed_field
    @property
    def missing_levels(self) -> list[str]:
        have = {entry.level for entry in self.entries}
        return [LEVEL_LABEL[level] for level in (Level.CLASS_10, Level.CLASS_12) if level not in have]
