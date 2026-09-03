from __future__ import annotations

import random
from datetime import date

import pytest

from sqlalchemy import select

from app.auth import service as auth_service
from app.journal import runner as journal_runner
from app.db.base import session_scope
from app.db.models import User
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
    address = f"sarathi.fixture.{random.randint(100000, 999999)}@example.invalid"

    with session_scope() as session:
        row = students_repo.save_profile(session, profile)
        session.flush()
        students_repo.save_history(session, row, profile.education_history)
        session.add(User(email=address, password_hash="not-a-real-hash", student_id=row.id))
        made = row.id

    yield made

    with session_scope() as session:
        owner = session.scalar(select(User).where(User.student_id == made))
        if owner is not None:
            session.delete(owner)
        row = students_repo.get_student(session, made)
        if row is not None:
            session.delete(row)


@pytest.fixture(scope="session")
def student_with_no_account() -> int:
    profile = _graduate_profile()
    with session_scope() as session:
        row = students_repo.save_profile(session, profile)
        session.flush()
        made = row.id

    yield made

    with session_scope() as session:
        row = students_repo.get_student(session, made)
        if row is not None:
            session.delete(row)


@pytest.fixture(autouse=True)
def no_real_messages(monkeypatch):
    class Recorder:
        channel = "test"

        def __init__(self) -> None:
            self.sent: list = []

        def send(self, message):
            from datetime import datetime, timezone

            from app.delivery.messenger import SentMessage

            self.sent.append(message)
            return SentMessage(
                to=message.to,
                body=message.body,
                channel=self.channel,
                sent_at=datetime.now(timezone.utc),
            )

    recorder = Recorder()
    monkeypatch.setattr(journal_runner, "get_messenger", lambda: recorder)
    return recorder


A_QUIET_DAY = date(2026, 6, 1)
A_DAY_NEAR_A_DEADLINE = date(2026, 8, 29)


@pytest.fixture
def a_quiet_day() -> date:
    return A_QUIET_DAY


@pytest.fixture
def a_day_near_a_deadline() -> date:
    return A_DAY_NEAR_A_DEADLINE
