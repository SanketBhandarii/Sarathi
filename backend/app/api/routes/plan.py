from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_student_or_404
from app.db.models import Student
from app.db.repositories import documents as docs_repo
from app.db.repositories import students as students_repo
from app.eligibility.age_cliff import AgeCliff, find_age_cliff
from app.eligibility.clashes import Clash, find_clashes
from app.eligibility.deadlines import UpcomingDeadline, upcoming_deadlines
from app.eligibility.radar import build_radar
from app.student.certificates import Certificate, CertificateWarning, check_certificates
from app.student.form_pack import FormPack, build_form_pack

router = APIRouter(prefix="/students", tags=["plan"])


@router.get("/{student_id}/deadlines", response_model=list[UpcomingDeadline])
def read_deadlines(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
    today: date | None = Query(default=None),
    within_days: int = Query(default=120, ge=1, le=400),
) -> list[UpcomingDeadline]:
    when = today or date.today()
    profile = students_repo.to_profile(student)
    radar = build_radar(
        profile, docs_repo.all_rules(db), docs_repo.all_calendar(db), today=when
    )
    return upcoming_deadlines(radar, when, within_days=within_days)


@router.get("/{student_id}/age-cliff", response_model=AgeCliff)
def read_age_cliff(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
    today: date | None = Query(default=None),
    horizon_years: int = Query(default=3, ge=1, le=10),
) -> AgeCliff:
    profile = students_repo.to_profile(student)
    return find_age_cliff(
        profile, docs_repo.all_rules(db), today or date.today(), horizon_years=horizon_years
    )


@router.get("/{student_id}/clashes", response_model=list[Clash])
def read_clashes(
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db),
    today: date | None = Query(default=None),
) -> list[Clash]:
    when = today or date.today()
    profile = students_repo.to_profile(student)
    radar = build_radar(
        profile, docs_repo.all_rules(db), docs_repo.all_calendar(db), today=when
    )
    return find_clashes(radar, when)


@router.post("/{student_id}/certificates/check", response_model=list[CertificateWarning])
def check_student_certificates(
    certificates: list[Certificate],
    student: Student = Depends(get_student_or_404),
    today: date | None = Query(default=None),
) -> list[CertificateWarning]:
    return check_certificates(certificates, today or date.today())


@router.get("/{student_id}/form-pack", response_model=FormPack)
def read_form_pack(
    exam_name: str = Query(...),
    student: Student = Depends(get_student_or_404),
    today: date | None = Query(default=None),
) -> FormPack:
    profile = students_repo.to_profile(student)
    return build_form_pack(profile, exam_name, today or date.today())
