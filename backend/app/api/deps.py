from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_session_factory
from app.db.models import Student
from app.db.repositories import students as students_repo


def get_db() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_student_or_404(student_id: int, db: Session = Depends(get_db)) -> Student:
    student = students_repo.get_student(db, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no student with id {student_id}",
        )
    return student
