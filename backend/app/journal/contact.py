from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


def where_to_write(session: Session, student_id: int) -> str | None:
    return session.scalar(select(User.email).where(User.student_id == student_id))
