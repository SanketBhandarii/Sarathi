from __future__ import annotations

from datetime import date

from app.eligibility.savings import find_savings
from app.extraction.schema import ApplicationFee, Citation, ExamRules
from app.student.profile import Category, Education, Gender, StudentProfile

CITE = Citation(page=15, quote="Rs. 175 for SC/ST/PwBD, Rs. 850 for all others")


def rules() -> list[ExamRules]:
    return [
        ExamRules(
            exam_name="Bank Exam", source_id="ibps", document_sha256="abc",
            fees=[
                ApplicationFee(amount_rupees=175, applies_to="SC/ST/PwBD candidates", citation=CITE),
                ApplicationFee(amount_rupees=850, applies_to="all others", citation=CITE),
            ],
        )
    ]


def student(category: Category, pwbd: bool = False) -> StudentProfile:
    return StudentProfile(
        name="T", date_of_birth=date(2004, 1, 1), category=category, is_pwbd=pwbd,
        gender=Gender.MALE, state="Maharashtra", district="Nagpur",
        education=Education(degree="B.Tech", percentage=60.0),
    )


def test_a_reserved_student_saves_money():
    summary = find_savings(student(Category.SC), rules())
    assert summary.total_saved == 675
    assert "675" in summary.message


def test_a_general_student_saves_nothing():
    summary = find_savings(student(Category.UR), rules())
    assert summary.savings == []
    assert "do not get a fee concession" in summary.message


def test_obc_gets_no_concession_when_the_notification_does_not_offer_one():
    assert find_savings(student(Category.OBC), rules()).savings == []


def test_pwbd_is_matched_even_when_listed_with_other_groups():
    summary = find_savings(student(Category.UR, pwbd=True), rules())
    assert summary.total_saved == 675


def test_saving_is_explained_in_plain_words():
    saving = find_savings(student(Category.ST), rules()).savings[0]
    assert "instead of" in saving.plain_words
    assert saving.citation is not None
