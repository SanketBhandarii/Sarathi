from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.eligibility.layers import Layer
from app.eligibility.verdict import Bucket
from app.student.profile import Category, Gender


class EducationIn(BaseModel):
    degree: str
    stream: str | None = None
    completed_year: int | None = None
    percentage: float | None = None
    is_completed: bool = True


class StudentIn(BaseModel):
    name: str
    date_of_birth: date
    category: Category = Category.UR
    gender: Gender = Gender.MALE
    is_pwbd: bool = False
    is_ex_serviceman: bool = False
    state: str
    district: str
    education: EducationIn


class StudentOut(StudentIn):
    id: int
    age_today: float


class CitationOut(BaseModel):
    page: int
    quote: str


class ReasonOut(BaseModel):
    text: str
    citation: CitationOut | None = None
    blocks_application: bool = False
    is_permanent: bool = False


class RadarEntryOut(BaseModel):
    exam_name: str
    source_id: str
    bucket: Bucket
    headline: str
    layer: Layer
    layer_label: str
    reasons: list[ReasonOut] = []
    rules_known: bool
    closing_text: str | None = None
    closing_on: date | None = None
    fee_payable: float | None = None
    unchecked: list[str] = []


class RadarOut(BaseModel):
    student_name: str
    generated_on: date
    total_watched: int
    counts: dict[str, int] = Field(default_factory=dict)
    entries: list[RadarEntryOut] = []
