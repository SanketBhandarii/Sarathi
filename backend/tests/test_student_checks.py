from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.eligibility.clashes import find_clashes
from app.eligibility.radar import Radar, RadarEntry
from app.eligibility.verdict import Bucket
from app.main import app
from app.student.certificates import (
    Certificate,
    CertificateType,
    check_certificates,
    financial_year_start,
)
from app.student.form_pack import build_form_pack
from app.student.samples import RAVI

TODAY = date(2026, 8, 30)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def entry(name: str, closes: date | None, bucket=Bucket.APPLY_NOW) -> RadarEntry:
    return RadarEntry(
        exam_name=name, source_id="ssc", bucket=bucket, rules_known=True, closing_on=closes
    )


def test_two_exams_on_the_same_day_are_a_clash():
    radar = Radar(
        student_name="T", generated_on=TODAY,
        entries=[entry("Exam A", date(2026, 10, 12)), entry("Exam B", date(2026, 10, 12))],
    )
    clashes = find_clashes(radar, TODAY)
    assert len(clashes) == 1
    assert "12 October 2026" in clashes[0].plain_words
    assert "only one" in clashes[0].plain_words


def test_exams_on_different_days_do_not_clash():
    radar = Radar(
        student_name="T", generated_on=TODAY,
        entries=[entry("Exam A", date(2026, 10, 12)), entry("Exam B", date(2026, 11, 2))],
    )
    assert find_clashes(radar, TODAY) == []


def test_past_dates_are_not_reported_as_clashes():
    radar = Radar(
        student_name="T", generated_on=TODAY,
        entries=[entry("Exam A", date(2026, 1, 1)), entry("Exam B", date(2026, 1, 1))],
    )
    assert find_clashes(radar, TODAY) == []


def test_financial_year_starts_in_april():
    assert financial_year_start(date(2026, 8, 30)) == date(2026, 4, 1)
    assert financial_year_start(date(2026, 2, 10)) == date(2025, 4, 1)


def test_last_years_obc_certificate_is_flagged():
    warnings = check_certificates(
        [Certificate(kind=CertificateType.OBC_NCL, issued_on=date(2025, 6, 1))], TODAY
    )
    assert len(warnings) == 1
    assert "Get a new one" in warnings[0].plain_words


def test_this_years_ews_certificate_is_fine():
    assert check_certificates(
        [Certificate(kind=CertificateType.EWS, issued_on=date(2026, 5, 10))], TODAY
    ) == []


def test_a_caste_certificate_never_expires():
    assert check_certificates(
        [Certificate(kind=CertificateType.CASTE, issued_on=date(2010, 1, 1))], TODAY
    ) == []


def test_form_pack_fills_what_it_knows_and_asks_for_the_rest():
    pack = build_form_pack(RAVI, "IBPS PO 2026", TODAY)
    assert pack.ready_count >= 10
    assert pack.needs_you_count >= 3
    filled = {f.label: f.value for f in pack.fields if not f.needs_you}
    assert filled["Full name"] == RAVI.name
    assert filled["Category"] == "OBC (Non-Creamy Layer)"
    assert filled["Date of birth"] == "14/11/2004"


def test_form_pack_warns_about_cgpa_versus_percentage():
    pack = build_form_pack(RAVI, "IBPS PO 2026", TODAY)
    marks = next(f for f in pack.fields if f.label == "Percentage of marks")
    assert "CGPA" in (marks.note or "")


def test_form_pack_endpoint(client):
    body = client.get(
        "/students/1/form-pack", params={"exam_name": "Test", "today": "2026-08-30"}
    ).json()
    assert body["ready_count"] >= 10
