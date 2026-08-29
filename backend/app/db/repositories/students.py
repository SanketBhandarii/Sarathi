from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Student
from app.student.profile import Category, Education, Gender, StudentProfile


def to_profile(row: Student) -> StudentProfile:
    return StudentProfile(
        name=row.name,
        date_of_birth=row.date_of_birth,
        category=Category(row.category),
        gender=Gender(row.gender),
        is_pwbd=row.is_pwbd,
        is_ex_serviceman=row.is_ex_serviceman,
        state=row.state,
        district=row.district,
        education=Education(
            degree=row.degree,
            stream=row.stream,
            completed_year=row.completed_year,
            percentage=row.percentage,
            is_completed=row.is_completed,
        ),
    )


def save_profile(session: Session, profile: StudentProfile, student_id: int | None = None) -> Student:
    row = session.get(Student, student_id) if student_id else None
    if row is None:
        row = Student()
        session.add(row)

    row.name = profile.name
    row.date_of_birth = profile.date_of_birth
    row.category = profile.category.value
    row.gender = profile.gender.value
    row.is_pwbd = profile.is_pwbd
    row.is_ex_serviceman = profile.is_ex_serviceman
    row.state = profile.state
    row.district = profile.district
    row.degree = profile.education.degree
    row.stream = profile.education.stream
    row.completed_year = profile.education.completed_year
    row.percentage = profile.education.percentage
    row.is_completed = profile.education.is_completed
    return row


def get_student(session: Session, student_id: int) -> Student | None:
    return session.get(Student, student_id)


def first_student(session: Session) -> Student | None:
    return session.scalar(select(Student).order_by(Student.id).limit(1))
