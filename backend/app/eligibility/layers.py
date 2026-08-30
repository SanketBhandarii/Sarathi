from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from app.student.profile import StudentProfile


class Layer(StrEnum):
    CENTRAL = "central"
    YOUR_STATE = "your_state"
    YOUR_CITY = "your_city"
    OPEN_TO_ALL_STATES = "open_to_all_states"
    ANOTHER_STATE = "another_state"


LAYER_LABEL: dict[Layer, str] = {
    Layer.CENTRAL: "Central government, open to every Indian",
    Layer.YOUR_STATE: "Your state",
    Layer.YOUR_CITY: "Your city and district",
    Layer.OPEN_TO_ALL_STATES: "Other states, open to everyone",
    Layer.ANOTHER_STATE: "Another state, needs their domicile",
}


class SourceProfile(BaseModel):
    source_id: str
    display_name: str
    state: str | None = None
    city: str | None = None
    needs_domicile: bool = False


SOURCE_PROFILES: dict[str, SourceProfile] = {
    "ssc": SourceProfile(source_id="ssc", display_name="Staff Selection Commission"),
    "upsc": SourceProfile(source_id="upsc", display_name="Union Public Service Commission"),
    "ibps": SourceProfile(source_id="ibps", display_name="Institute of Banking Personnel Selection"),
    "mpsc": SourceProfile(
        source_id="mpsc",
        display_name="Maharashtra Public Service Commission",
        state="Maharashtra",
        needs_domicile=True,
    ),
    "bmc": SourceProfile(
        source_id="bmc",
        display_name="Brihanmumbai Municipal Corporation",
        state="Maharashtra",
        city="Mumbai",
        needs_domicile=True,
    ),
}


def profile_for(source_id: str) -> SourceProfile:
    return SOURCE_PROFILES.get(
        source_id, SourceProfile(source_id=source_id, display_name=source_id.upper())
    )


def _same(left: str | None, right: str | None) -> bool:
    return bool(left) and bool(right) and left.strip().lower() == right.strip().lower()


def layer_for(source_id: str, student: StudentProfile) -> Layer:
    source = profile_for(source_id)

    if source.state is None:
        return Layer.CENTRAL
    if not source.needs_domicile:
        return Layer.OPEN_TO_ALL_STATES
    if not _same(source.state, student.state):
        return Layer.ANOTHER_STATE
    if source.city:
        return Layer.YOUR_CITY
    return Layer.YOUR_STATE


def domicile_blocks(source_id: str, student: StudentProfile) -> str | None:
    source = profile_for(source_id)
    if source.state is None or not source.needs_domicile:
        return None
    if _same(source.state, student.state):
        return None
    return (
        f"This one is only for people from {source.state}. "
        f"You are from {student.state}."
    )
