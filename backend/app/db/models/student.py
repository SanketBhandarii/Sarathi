from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    date_of_birth: Mapped[date] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(8), default="UR")
    gender: Mapped[str] = mapped_column(String(16), default="male")
    is_pwbd: Mapped[bool] = mapped_column(Boolean, default=False)
    is_ex_serviceman: Mapped[bool] = mapped_column(Boolean, default=False)

    state: Mapped[str] = mapped_column(String(64))
    district: Mapped[str] = mapped_column(String(64))

    degree: Mapped[str] = mapped_column(String(64))
    stream: Mapped[str | None] = mapped_column(String(96), nullable=True)
    completed_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True)

    language: Mapped[str] = mapped_column(String(8), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    journal_runs: Mapped[list["JournalRun"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    deadlines: Mapped[list["Deadline"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    qualifications: Mapped[list["QualificationRecord"]] = relationship(
        back_populates="student", cascade="all, delete-orphan", lazy="selectin"
    )


from app.db.models.journal import Deadline, JournalRun  # noqa: E402
from app.db.models.qualification import QualificationRecord  # noqa: E402
