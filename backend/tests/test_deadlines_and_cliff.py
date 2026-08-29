from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.eligibility.age_cliff import find_age_cliff
from app.extraction.schema import AgeRelaxation, AgeRule, Citation, ExamRules
from app.main import app
from app.student.profile import Category, Education, StudentProfile

TODAY = date(2026, 8, 29)
CITE = Citation(page=6, quote="Minimum: 20 years Maximum: 30 years")


def rules() -> list[ExamRules]:
    return [
        ExamRules(
            exam_name="Test Bank Exam", source_id="ibps", document_sha256="abc",
            age=AgeRule(minimum_years=20, maximum_years=30, citation=CITE),
            age_relaxations=[
                AgeRelaxation(category="Other Backward Classes", extra_years=3, citation=CITE)
            ],
        )
    ]


def student(born: date, category: Category = Category.UR) -> StudentProfile:
    return StudentProfile(
        name="Test", date_of_birth=born, category=category,
        state="Maharashtra", district="Nagpur",
        education=Education(degree="B.Com", percentage=62.0),
    )


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_a_young_student_has_no_age_cliff_yet():
    cliff = find_age_cliff(student(date(2004, 11, 14)), rules(), TODAY, horizon_years=1)
    assert cliff.has_warning is False


def test_relaxation_pushes_the_cliff_further_away():
    born = date(1996, 11, 14)
    general = find_age_cliff(student(born, Category.UR), rules(), TODAY, horizon_years=8)
    obc = find_age_cliff(student(born, Category.OBC), rules(), TODAY, horizon_years=8)

    assert general.exams_closing[0].limit_for_you == 30
    assert obc.exams_closing[0].limit_for_you == 33
    assert obc.exams_closing[0].closes_on > general.exams_closing[0].closes_on


def test_someone_already_past_the_limit_is_not_warned_again():
    cliff = find_age_cliff(student(date(1980, 1, 1)), rules(), TODAY, horizon_years=8)
    assert cliff.exams_closing == []


def test_cliff_message_names_the_real_closing_date():
    cliff = find_age_cliff(student(date(1996, 11, 14), Category.UR), rules(), TODAY, horizon_years=8)
    assert "2027" in cliff.message
    assert "31" in cliff.message


def test_deadlines_endpoint_sorts_by_date_and_says_days_left(client):
    body = client.get("/students/1/deadlines", params={"today": "2026-08-29"}).json()
    assert body
    assert [d["due_on"] for d in body] == sorted(d["due_on"] for d in body)
    for item in body:
        assert item["days_left"] >= 0
        assert item["urgency"] in {"today", "this week", "this month", "later"}
        assert item["plain_words"]


def test_deadlines_respect_the_window(client):
    narrow = client.get(
        "/students/1/deadlines", params={"today": "2026-08-29", "within_days": 14}
    ).json()
    wide = client.get(
        "/students/1/deadlines", params={"today": "2026-08-29", "within_days": 200}
    ).json()
    assert len(narrow) <= len(wide)


def test_age_cliff_endpoint_returns_a_message(client):
    body = client.get("/students/1/age-cliff", params={"today": "2026-08-29"}).json()
    assert body["message"]
    assert isinstance(body["has_warning"], bool)
