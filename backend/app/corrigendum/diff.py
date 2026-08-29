from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, computed_field

from app.extraction.schema import Citation, ExamRules


class ChangeKind(StrEnum):
    DATE_MOVED = "date_moved"
    AGE_CHANGED = "age_changed"
    RELAXATION_CHANGED = "relaxation_changed"
    FEE_CHANGED = "fee_changed"
    QUALIFICATION_CHANGED = "qualification_changed"
    RULE_ADDED = "rule_added"
    RULE_REMOVED = "rule_removed"


class RuleChange(BaseModel):
    kind: ChangeKind
    field: str
    told_you: str | None
    now_says: str | None
    old_citation: Citation | None = None
    new_citation: Citation | None = None

    @computed_field
    @property
    def is_worse_for_student(self) -> bool:
        return self.kind is ChangeKind.DATE_MOVED and _moved_earlier(self)

    @computed_field
    @property
    def plain_words(self) -> str:
        before = _readable(self.told_you)
        after = _readable(self.now_says)
        if self.told_you is None:
            return f"{self.field} is new: {after}."
        if self.now_says is None:
            return f"{self.field} has been removed. It used to say {before}."
        if self.is_worse_for_student:
            return (
                f"I told you {self.field} was {before}. It has moved earlier, "
                f"to {after}. You have less time than I said."
            )
        return f"I told you {self.field} was {before}. It is now {after}."


def _readable(value: str | None) -> str:
    if value is None:
        return "nothing"
    try:
        return date.fromisoformat(value).strftime("%d %B %Y")
    except ValueError:
        pass
    try:
        number = float(value)
        return f"{number:g}"
    except ValueError:
        return value


def _moved_earlier(change: RuleChange) -> bool:
    try:
        return date.fromisoformat(str(change.now_says)) < date.fromisoformat(str(change.told_you))
    except (ValueError, TypeError):
        return False


class Corrigendum(BaseModel):
    exam_name: str
    source_id: str
    old_document_sha256: str
    new_document_sha256: str
    changes: list[RuleChange] = []

    @computed_field
    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @computed_field
    @property
    def apology(self) -> str:
        if not self.changes:
            return f"Nothing has changed in {self.exam_name}."
        urgent = [c for c in self.changes if c.is_worse_for_student]
        opening = (
            "The commission has changed this exam, and one change makes you late."
            if urgent
            else "The commission has changed this exam after I last told you about it."
        )
        return f"{opening} I was wrong. Here is the correction."
