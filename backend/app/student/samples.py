from __future__ import annotations

from datetime import date

from app.student.profile import Category, Education, Gender, StudentProfile

RAVI = StudentProfile(
    name="Ravi Patil",
    date_of_birth=date(2004, 11, 14),
    category=Category.OBC,
    gender=Gender.MALE,
    state="Maharashtra",
    district="Nagpur",
    education=Education(
        degree="B.Tech",
        stream="Computer Science",
        completed_year=2026,
        percentage=58.0,
        is_completed=True,
    ),
    attempts_used={"SSC CGL": 2},
)
