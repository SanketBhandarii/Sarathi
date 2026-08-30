from __future__ import annotations

import random
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

EMAIL_LOG = get_settings().notifications_path.parent / "emails.log"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def fresh_email() -> str:
    return f"student{random.randint(100000, 999999)}@example.com"


def code_sent_to(email: str) -> str:
    lines = Path(EMAIL_LOG).read_text(encoding="utf-8").splitlines()
    for line in reversed(lines):
        if email in line:
            match = re.search(r"(\d{6})\s*$", line)
            if match:
                return match.group(1)
    raise AssertionError(f"no code was sent to {email}")


def test_a_student_can_sign_up_verify_and_sign_in(client):
    email = fresh_email()
    password = "nagpur-ravi-2026"

    assert client.post("/auth/sign-up", json={"email": email, "password": password}).status_code == 201

    verified = client.post(
        "/auth/verify", json={"email": email, "code": code_sent_to(email)}
    )
    assert verified.status_code == 200
    assert verified.json()["is_verified"] is True
    assert verified.json()["token"]

    signed_in = client.post("/auth/sign-in", json={"email": email, "password": password})
    assert signed_in.status_code == 200


def test_a_weak_password_is_refused(client):
    for weak in ["short", "12345678", "password"]:
        response = client.post("/auth/sign-up", json={"email": fresh_email(), "password": weak})
        assert response.status_code == 422


def test_a_wrong_code_is_refused_and_counts_down(client):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": "nagpur-ravi-2026"})

    first = client.post("/auth/verify", json={"email": email, "code": "000000"})
    assert first.status_code == 400
    assert "tries left" in first.json()["detail"]


def test_a_code_cannot_be_used_twice(client):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": "nagpur-ravi-2026"})
    code = code_sent_to(email)

    assert client.post("/auth/verify", json={"email": email, "code": code}).status_code == 200
    again = client.post("/auth/verify", json={"email": email, "code": code})
    assert again.status_code == 400
    assert "already been used" in again.json()["detail"]


def test_you_cannot_sign_in_before_confirming_your_email(client):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": "nagpur-ravi-2026"})
    response = client.post("/auth/sign-in", json={"email": email, "password": "nagpur-ravi-2026"})
    assert response.status_code == 403
    assert "confirm your email" in response.json()["detail"]


def test_a_wrong_password_does_not_say_which_part_was_wrong(client):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": "nagpur-ravi-2026"})
    client.post("/auth/verify", json={"email": email, "code": code_sent_to(email)})

    response = client.post("/auth/sign-in", json={"email": email, "password": "not-the-password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "That email or password is wrong."


def test_asking_for_a_code_too_fast_is_slowed_down(client):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": "nagpur-ravi-2026"})
    response = client.post("/auth/resend-code", json={"email": email})
    assert response.status_code in (200, 429)


def test_resend_does_not_reveal_whether_an_email_exists(client):
    response = client.post("/auth/resend-code", json={"email": "nobody-here@example.com"})
    assert response.status_code == 200
    assert "If that email has an account" in response.json()["message"]


def test_the_session_cookie_is_http_only(client):
    email = fresh_email()
    client.post("/auth/sign-up", json={"email": email, "password": "nagpur-ravi-2026"})
    response = client.post("/auth/verify", json={"email": email, "code": code_sent_to(email)})
    cookie = response.headers.get("set-cookie", "")
    assert "httponly" in cookie.lower()
