from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class Citation(BaseModel):
    page: int = Field(description="1-based page number these words appear on")
    quote: str = Field(description="the sentence copied word for word from that page")


class AgeRule(BaseModel):
    minimum_years: int | None = None
    maximum_years: int | None = None
    reckoned_on: date | None = Field(default=None, description="the date age is counted as on")
    citation: Citation


class AgeRelaxation(BaseModel):
    category: str = Field(description="SC, ST, OBC, PwBD, Ex-Servicemen or as printed")
    extra_years: int
    citation: Citation


class AgeSection(BaseModel):
    age: AgeRule
    relaxations: list[AgeRelaxation] = []


class Qualification(BaseModel):
    requirement: str = Field(description="what degree is needed, in plain words")
    minimum_percentage: float | None = None
    citation: Citation


class QualificationSection(BaseModel):
    qualifications: list[Qualification] = []


class ApplicationFee(BaseModel):
    amount_rupees: float
    applies_to: str = Field(description="which candidates pay this amount")
    citation: Citation


class FeeSection(BaseModel):
    fees: list[ApplicationFee] = []


class KeyDate(BaseModel):
    label: str = Field(description="what happens, in plain words")
    happens_on: date
    citation: Citation


class DateSection(BaseModel):
    key_dates: list[KeyDate] = []


class ExamRules(BaseModel):
    exam_name: str
    source_id: str
    document_sha256: str
    age: AgeRule | None = None
    age_relaxations: list[AgeRelaxation] = []
    qualifications: list[Qualification] = []
    fees: list[ApplicationFee] = []
    key_dates: list[KeyDate] = []

    def all_citations(self) -> list[Citation]:
        cited = [self.age.citation] if self.age else []
        for group in (self.age_relaxations, self.qualifications, self.fees, self.key_dates):
            cited.extend(item.citation for item in group)
        return cited
