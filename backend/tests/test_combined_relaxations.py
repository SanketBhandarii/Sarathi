from __future__ import annotations

from datetime import date

import pytest

from app.eligibility.categories import best_relaxation_years, label_applies_to
from app.student.profile import Category, Education, Gender, StudentProfile


def _student(**changes) -> StudentProfile:
    base = dict(
        name="Ravi Patil",
        date_of_birth=date(2004, 11, 14),
        category=Category.OBC,
        gender=Gender.MALE,
        state="Maharashtra",
        district="Nagpur",
        education=Education(degree="Graduation", is_completed=True),
    )
    base.update(changes)
    return StudentProfile(**base)


def test_a_row_meant_for_disabled_obc_does_not_apply_to_an_obc_who_is_not_disabled():
    assert label_applies_to("Persons with Disabilities (PwD) + OBC", _student()) is False


def test_that_same_row_applies_to_an_obc_who_is_disabled():
    assert label_applies_to("Persons with Disabilities (PwD) + OBC", _student(is_pwbd=True)) is True


def test_a_plain_obc_row_still_applies():
    assert label_applies_to("Other Backward Classes (Non-Creamy Layer)", _student()) is True


def test_a_row_naming_two_categories_applies_to_either_one():
    assert label_applies_to("SC/ST", _student(category=Category.SC)) is True
    assert label_applies_to("SC/ST", _student(category=Category.ST)) is True
    assert label_applies_to("SC/ST", _student(category=Category.OBC)) is False


def test_a_general_row_does_not_apply_to_an_obc_candidate():
    assert label_applies_to("Unreserved", _student()) is False


def test_a_slash_list_means_any_one_of_them():
    label = "SC/ST/PwBD candidates"
    assert label_applies_to(label, _student(category=Category.SC)) is True
    assert label_applies_to(label, _student(is_pwbd=True)) is True
    assert label_applies_to(label, _student()) is False


def test_a_plus_sign_means_the_same_person_is_both():
    label = "Persons with Disabilities (PwD) + OBC"
    assert label_applies_to(label, _student()) is False
    assert label_applies_to(label, _student(is_pwbd=True)) is True
    assert label_applies_to(label, _student(category=Category.SC, is_pwbd=True)) is False


def test_a_women_row_applies_only_to_women():
    assert label_applies_to("Women candidates", _student()) is False
    assert label_applies_to("Women candidates", _student(gender=Gender.FEMALE)) is True


def test_an_ex_serviceman_obc_row_needs_both():
    label = "Ex-Servicemen belonging to OBC"
    assert label_applies_to(label, _student()) is False
    assert label_applies_to(label, _student(is_ex_serviceman=True)) is True


def test_it_picks_three_years_not_thirteen_for_an_obc_who_is_not_disabled():
    rows = [
        ("Other Backward Classes (Non-Creamy Layer)", 3),
        ("Scheduled Caste / Scheduled Tribe", 5),
        ("Persons with Disabilities (PwD) + OBC", 13),
        ("Persons with Disabilities (PwD) + UR", 10),
    ]
    years, label = best_relaxation_years(rows, _student())
    assert years == 3
    assert label is not None and "Backward" in label


def test_it_picks_thirteen_years_for_an_obc_who_is_disabled():
    rows = [
        ("Other Backward Classes (Non-Creamy Layer)", 3),
        ("Persons with Disabilities (PwD) + OBC", 13),
    ]
    years, _ = best_relaxation_years(rows, _student(is_pwbd=True))
    assert years == 13


def test_a_row_naming_nothing_we_know_applies_to_nobody():
    assert label_applies_to("Departmental candidates only", _student()) is False


@pytest.mark.parametrize("category", list(Category))
def test_no_student_ever_gets_a_relaxation_meant_for_another_category(category):
    rows = [(other.value, 5) for other in Category if other is not category]
    years, label = best_relaxation_years(rows, _student(category=category))
    assert years == 0
    assert label is None
