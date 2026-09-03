from __future__ import annotations

import base64
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

PASSWORD = "nagpur-ravi-2026"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def signed_in(client, no_real_email, fresh_email):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": PASSWORD})
    token = client.post(
        "/auth/verify", json={"email": email, "code": no_real_email.codes[email]}
    ).json()["token"]

    client.post(
        "/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Ravi Patil",
            "date_of_birth": "2004-11-14",
            "category": "OBC",
            "gender": "male",
            "state": "Maharashtra",
            "district": "Nagpur",
            "qualifications": [
                {"level": "class_10", "marks": 78.4, "passed_year": 2020, "is_completed": True}
            ],
        },
    )
    return token


def a_picture(width: int, height: int) -> bytes:
    canvas = Image.new("RGB", (width, height), (170, 180, 200))
    for x in range(0, width, 7):
        for y in range(0, height, 5):
            canvas.putpixel((x, y), (40, 40, 60))
    holder = io.BytesIO()
    canvas.save(holder, format="JPEG", quality=92)
    return holder.getvalue()


def upload(client, token: str, kind: str, payload: bytes):
    return client.post(
        f"/me/documents/{kind}",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (f"{kind}.jpg", payload, "image/jpeg")},
    )


def test_a_student_uploads_one_photo_and_gets_every_commission_size(client, signed_in):
    assert upload(client, signed_in, "photograph", a_picture(900, 1200)).status_code == 201

    response = client.get(
        "/me/documents/photograph/sizes", headers={"Authorization": f"Bearer {signed_in}"}
    )
    assert response.status_code == 200

    made = response.json()
    assert len(made) >= 4

    for one in made:
        picture = Image.open(io.BytesIO(base64.b64decode(one["image_base64"])))
        assert picture.format == "JPEG"
        assert picture.width == one["width_px"]
        assert picture.height == one["height_px"]
        assert one["matches"] is True


def test_the_sizes_actually_differ_between_commissions(client, signed_in):
    upload(client, signed_in, "photograph", a_picture(900, 1200))
    made = client.get(
        "/me/documents/photograph/sizes", headers={"Authorization": f"Bearer {signed_in}"}
    ).json()

    shapes = {(one["width_px"], one["height_px"]) for one in made}
    assert len(shapes) > 1


def test_a_signature_is_made_at_its_own_shape_not_the_photo_shape(client, signed_in):
    upload(client, signed_in, "photograph", a_picture(900, 1200))
    upload(client, signed_in, "signature", a_picture(1200, 400))

    photos = client.get(
        "/me/documents/photograph/sizes", headers={"Authorization": f"Bearer {signed_in}"}
    ).json()
    signatures = client.get(
        "/me/documents/signature/sizes", headers={"Authorization": f"Bearer {signed_in}"}
    ).json()

    for one in signatures:
        assert one["width_px"] > one["height_px"]
    for one in photos:
        assert one["height_px"] > one["width_px"]


def test_asking_for_sizes_before_uploading_says_so_instead_of_failing_quietly(client, signed_in):
    response = client.get(
        "/me/documents/thumb_impression/sizes",
        headers={"Authorization": f"Bearer {signed_in}"},
    )
    assert response.status_code == 404
    assert "first" in response.json()["detail"].lower()


def test_the_pdf_sheet_downloads_and_is_a_real_pdf(client, signed_in):
    upload(client, signed_in, "photograph", a_picture(900, 1200))

    response = client.get(
        "/me/documents/sheet", headers={"Authorization": f"Bearer {signed_in}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 20_000
    assert "attachment" in response.headers["content-disposition"]


def test_the_pdf_sheet_works_even_before_any_picture_is_added(client, signed_in):
    response = client.get(
        "/me/documents/sheet", headers={"Authorization": f"Bearer {signed_in}"}
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")


def test_a_second_upload_replaces_the_first(client, signed_in):
    upload(client, signed_in, "photograph", a_picture(900, 1200))
    upload(client, signed_in, "photograph", a_picture(600, 800))

    listed = client.get(
        "/me/documents", headers={"Authorization": f"Bearer {signed_in}"}
    ).json()
    photos = [one for one in listed if one["kind"] == "photograph"]
    assert len(photos) == 1
    assert photos[0]["width_px"] == 600


def test_nobody_can_read_documents_without_signing_in(client):
    assert client.get("/me/documents").status_code == 401
    assert client.get("/me/documents/photograph/sizes").status_code == 401
    assert client.get("/me/documents/sheet").status_code == 401
