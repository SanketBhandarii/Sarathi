from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class EventKind(StrEnum):
    SOURCE_CHECKED = "source_checked"
    NOTIFICATION_SEEN = "notification_seen"
    DOCUMENT_READ = "document_read"
    CITATION_VERIFIED = "citation_verified"
    RULE_EVALUATED = "rule_evaluated"
    DEADLINE_NEAR = "deadline_near"
    NEWLY_ELIGIBLE = "newly_eligible"
    RULE_CHANGED = "rule_changed"
    NOTHING_TO_SAY = "nothing_to_say"


WORTH_TELLING = {
    EventKind.DEADLINE_NEAR,
    EventKind.NEWLY_ELIGIBLE,
    EventKind.RULE_CHANGED,
}


@dataclass
class Event:
    kind: EventKind
    detail: str

    @property
    def worth_telling(self) -> bool:
        return self.kind in WORTH_TELLING


@dataclass
class RunTally:
    sources_checked: int = 0
    notifications_seen: int = 0
    documents_downloaded: int = 0
    rules_evaluated: int = 0
    citations_verified: int = 0
    changes_found: int = 0
    events: list[Event] = field(default_factory=list)

    def add(self, event: Event) -> None:
        self.events.append(event)
        if event.worth_telling:
            self.changes_found += 1

    @property
    def messages_to_send(self) -> list[Event]:
        return [e for e in self.events if e.worth_telling]

    @property
    def checks_run(self) -> int:
        return self.rules_evaluated + self.citations_verified
