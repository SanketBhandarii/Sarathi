from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Category(StrEnum):
    UR = "UR"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    TRANSGENDER = "transgender"


class Education(BaseModel):
    degree: str
    stream: str | None = None
    completed_year: int | None = None
    percentage: float | None = None
    is_completed: bool = True


class StudentProfile(BaseModel):
    name: str
    date_of_birth: date
    category: Category = Category.UR
    gender: Gender = Gender.MALE
    is_pwbd: bool = False
    is_ex_serviceman: bool = False
    state: str
    district: str
    education: Education
    attempts_used: dict[str, int] = Field(default_factory=dict)

    def age_on(self, reference: date) -> float:
        years = reference.year - self.date_of_birth.year
        before_birthday = (reference.month, reference.day) < (
            self.date_of_birth.month,
            self.date_of_birth.day,
        )
        return years - (1 if before_birthday else 0)

    def turns(self, age: int) -> date:
        birthday = self.date_of_birth
        return date(birthday.year + age, birthday.month, birthday.day)
