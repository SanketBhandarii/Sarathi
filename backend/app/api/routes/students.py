from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_student_or_404
from app.api.schemas import EducationIn, StudentIn, StudentOut
from app.db.models import Student
from app.db.repositories import students as students_repo
from app.student.profile import Category, Education, Gender, StudentProfile

router = APIRouter(prefix="/students", tags=["students"])


def _to_out(row: Student) -> StudentOut:
    profile = students_repo.to_profile(row)
    return StudentOut(
        id=row.id,
        name=row.name,
        date_of_birth=row.date_of_birth,
        category=Category(row.category),
        gender=Gender(row.gender),
        is_pwbd=row.is_pwbd,
        is_ex_serviceman=row.is_ex_serviceman,
        state=row.state,
        district=row.district,
        education=EducationIn(
            degree=row.degree,
            stream=row.stream,
            completed_year=row.completed_year,
            percentage=row.percentage,
            is_completed=row.is_completed,
        ),
        age_today=profile.age_on(date.today()),
    )


@router.get("/{student_id}", response_model=StudentOut)
def read_student(student: Student = Depends(get_student_or_404)) -> StudentOut:
    return _to_out(student)


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    payload: StudentIn,
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
) -> StudentOut:
    profile = StudentProfile(
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        category=payload.category,
        gender=payload.gender,
        is_pwbd=payload.is_pwbd,
        is_ex_serviceman=payload.is_ex_serviceman,
        state=payload.state,
        district=payload.district,
        education=Education(**payload.education.model_dump()),
    )
    row = students_repo.save_profile(db, profile, student_id=student.id)
    db.flush()
    return _to_out(row)


@router.post("", response_model=StudentOut, status_code=201)
def create_student(payload: StudentIn, db: Session = Depends(get_db)) -> StudentOut:
    profile = StudentProfile(
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        category=payload.category,
        gender=payload.gender,
        is_pwbd=payload.is_pwbd,
        is_ex_serviceman=payload.is_ex_serviceman,
        state=payload.state,
        district=payload.district,
        education=Education(**payload.education.model_dump()),
    )
    row = students_repo.save_profile(db, profile)
    db.flush()
    return _to_out(row)
