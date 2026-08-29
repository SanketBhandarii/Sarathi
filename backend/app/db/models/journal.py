from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JournalRun(Base):
    __tablename__ = "journal_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sources_checked: Mapped[int] = mapped_column(Integer, default=0)
    notifications_seen: Mapped[int] = mapped_column(Integer, default=0)
    documents_downloaded: Mapped[int] = mapped_column(Integer, default=0)
    rules_evaluated: Mapped[int] = mapped_column(Integer, default=0)
    citations_verified: Mapped[int] = mapped_column(Integer, default=0)
    changes_found: Mapped[int] = mapped_column(Integer, default=0)
    messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    seconds_taken: Mapped[float] = mapped_column(default=0.0)

    student: Mapped["Student"] = relationship(back_populates="journal_runs")
    events: Mapped[list["JournalEvent"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )

    @property
    def was_silent(self) -> bool:
        return self.messages_sent == 0


class JournalEvent(Base):
    __tablename__ = "journal_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("journal_runs.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    detail: Mapped[str] = mapped_column(Text)
    worth_telling: Mapped[bool] = mapped_column(Boolean, default=False)

    run: Mapped["JournalRun"] = relationship(back_populates="events")


class Deadline(Base):
    __tablename__ = "deadlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    exam_name: Mapped[str] = mapped_column(Text)
    source_id: Mapped[str] = mapped_column(String(16))
    label: Mapped[str] = mapped_column(Text)
    due_on: Mapped[date] = mapped_column(Date, index=True)
    is_approximate: Mapped[bool] = mapped_column(Boolean, default=False)
    citation_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    citation_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)

    student: Mapped["Student"] = relationship(back_populates="deadlines")


from app.db.models.student import Student  # noqa: E402
