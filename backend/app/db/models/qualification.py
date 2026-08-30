from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QualificationRecord(Base):
    __tablename__ = "qualifications"
    __table_args__ = (UniqueConstraint("student_id", "level", name="uq_student_level"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    level: Mapped[str] = mapped_column(String(24))
    board_or_university: Mapped[str | None] = mapped_column(String(160), nullable=True)
    college: Mapped[str | None] = mapped_column(String(160), nullable=True)
    stream: Mapped[str | None] = mapped_column(String(120), nullable=True)
    marks_kind: Mapped[str] = mapped_column(String(16), default="percentage")
    marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    cgpa_scale: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True)
    current_semester: Mapped[int | None] = mapped_column(Integer, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="qualifications")


from app.db.models.student import Student  # noqa: E402
