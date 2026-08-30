from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import QualificationRecord, Student
from app.student.profile import Category, Education, Gender, StudentProfile
from app.student.qualifications import EducationHistory, Level, MarksKind, Qualification


def to_history(row: Student) -> EducationHistory:
    return EducationHistory(
        entries=[
            Qualification(
                level=Level(record.level),
                board_or_university=record.board_or_university,
                college=record.college,
                stream=record.stream,
                marks_kind=MarksKind(record.marks_kind),
                marks=record.marks,
                cgpa_scale=record.cgpa_scale,
                passed_year=record.passed_year,
                passed_on=record.passed_on,
                is_completed=record.is_completed,
                current_semester=record.current_semester,
            )
            for record in sorted(row.qualifications, key=lambda r: r.level)
        ]
    )


def save_history(session: Session, row: Student, history: EducationHistory) -> None:
    row.qualifications.clear()
    session.flush()
    for entry in history.entries:
        session.add(
            QualificationRecord(
                student_id=row.id,
                level=entry.level.value,
                board_or_university=entry.board_or_university,
                college=entry.college,
                stream=entry.stream,
                marks_kind=entry.marks_kind.value,
                marks=entry.marks,
                cgpa_scale=entry.cgpa_scale,
                passed_year=entry.passed_year,
                passed_on=entry.passed_on,
                is_completed=entry.is_completed,
                current_semester=entry.current_semester,
            )
        )
    session.flush()


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
        education_history=to_history(row),
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
