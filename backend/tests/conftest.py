from __future__ import annotations

import random
from datetime import date

import pytest

from app.auth import service as auth_service
from app.db.base import session_scope
from app.db.repositories import students as students_repo
from app.language.phrases import Language
from app.student.profile import Category, Education, Gender, StudentProfile
from app.student.qualifications import EducationHistory, Level, MarksKind
from app.student.qualifications import Qualification as Step


class CapturingMailer:
    def __init__(self) -> None:
        self.codes: dict[str, str] = {}

    def send_code(self, to: str, code: str, language: Language = Language.ENGLISH) -> None:
        self.codes[to.strip().lower()] = code


@pytest.fixture(autouse=True)
def no_real_email(monkeypatch):
    mailer = CapturingMailer()
    monkeypatch.setattr(auth_service, "get_mailer", lambda: mailer)
    return mailer


@pytest.fixture
def fresh_email():
    def make() -> str:
        return f"sarathi.test.{random.randint(100000, 999999)}@gmail.com"

    return make


def _graduate_profile() -> StudentProfile:
    return StudentProfile(
        name="Ravi Patil",
        date_of_birth=date(2004, 11, 14),
        category=Category.OBC,
        gender=Gender.MALE,
        state="Maharashtra",
        district="Nagpur",
        education=Education(
            degree="Graduation", stream="Computer Science",
            completed_year=2026, percentage=64.0, is_completed=True,
        ),
        education_history=EducationHistory(
            entries=[
                Step(level=Level.CLASS_10, marks=78.4, passed_year=2020, is_completed=True),
                Step(level=Level.CLASS_12, marks=71.2, passed_year=2022, is_completed=True),
                Step(
                    level=Level.GRADUATION, marks=6.4, marks_kind=MarksKind.CGPA,
                    cgpa_scale=10, passed_year=2026, is_completed=True,
                ),
            ]
        ),
    )


@pytest.fixture(scope="session")
def student_id() -> int:
    profile = _graduate_profile()
    with session_scope() as session:
        row = students_repo.save_profile(session, profile)
        session.flush()
        students_repo.save_history(session, row, profile.education_history)
        made = row.id

    yield made

    with session_scope() as session:
        row = students_repo.get_student(session, made)
        if row is not None:
            session.delete(row)
