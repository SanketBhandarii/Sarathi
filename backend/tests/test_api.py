from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def sample_photo(width: int = 1800, height: int = 2400) -> bytes:
    image = Image.new("RGB", (width, height), (240, 242, 250))
    draw = ImageDraw.Draw(image)
    draw.ellipse([width // 5, height // 6, 4 * width // 5, 3 * height // 5], fill=(205, 175, 145))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def test_health_reports_what_is_in_the_database(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["students"] >= 1
    assert body["documents"] >= 1


def test_student_profile_is_returned(client):
    body = client.get("/students/1").json()
    assert body["name"]
    assert body["state"]
    assert body["age_today"] > 0


def test_unknown_student_gives_404(client):
    assert client.get("/students/999999").status_code == 404


def test_radar_returns_buckets_and_layers(client):
    body = client.get("/students/1/radar", params={"today": "2026-08-29"}).json()
    assert body["total_watched"] >= 1
    assert body["counts"]
    for entry in body["entries"]:
        assert entry["headline"]
        assert entry["layer_label"]


def test_radar_reasons_carry_citations_where_rules_are_known(client):
    body = client.get("/students/1/radar", params={"today": "2026-08-29"}).json()
    known = [e for e in body["entries"] if e["rules_known"]]
    assert known
    cited = [r for e in known for r in e["reasons"] if r.get("citation")]
    assert cited
    for reason in cited:
        assert reason["citation"]["page"] > 0
        assert len(reason["citation"]["quote"]) > 10


def test_exam_detail_exposes_the_rules(client):
    exams = client.get("/exams").json()
    readable = [e for e in exams if e["readable"]]
    assert readable
    detail = client.get(f"/exams/{readable[0]['document_sha256']}").json()
    assert detail["exam_name"]
    assert detail["citation_count"] >= 1


def test_document_maker_endpoint_hits_the_spec(client):
    response = client.post(
        "/documents/make",
        files={"file": ("photo.jpg", sample_photo(), "image/jpeg")},
        data={"kind": "photograph", "width_px": 200, "height_px": 230,
              "min_kb": 20, "max_kb": 50},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["matches_spec"] is True
    assert body["width_px"] == 200 and body["height_px"] == 230
    assert 20 <= body["size_kb"] <= 50
    assert body["image_base64"]


def test_document_maker_rejects_a_non_image(client):
    response = client.post(
        "/documents/make",
        files={"file": ("notes.txt", b"this is not an image", "text/plain")},
        data={"kind": "photograph", "width_px": 200, "height_px": 230,
              "min_kb": 20, "max_kb": 50},
    )
    assert response.status_code == 400
