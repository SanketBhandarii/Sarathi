from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "nagpur-ravi-2026"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def sign_up(client, email: str):
    return client.post("/auth/sign-up", json={"email": email, "password": PASSWORD})


def test_a_student_can_sign_up_verify_and_sign_in(client, no_real_email, fresh_email):
    email = fresh_email()
    assert sign_up(client, email).status_code == 201

    code = no_real_email.codes[email]
    verified = client.post("/auth/verify", json={"email": email, "code": code})
    assert verified.status_code == 200
    assert verified.json()["is_verified"] is True
    assert verified.json()["token"]

    assert client.post("/auth/sign-in", json={"email": email, "password": PASSWORD}).status_code == 200


def test_a_weak_password_is_refused(client, fresh_email):
    for weak in ["short", "12345678", "password"]:
        response = client.post("/auth/sign-up", json={"email": fresh_email(), "password": weak})
        assert response.status_code == 422


@pytest.mark.parametrize(
    "email",
    ["ravi@mailinator.com", "someone@example.com", "not-an-email", "x@no-such-domain-xyz9.com"],
)
def test_fake_or_undeliverable_emails_are_refused(client, email):
    assert client.post("/auth/sign-up", json={"email": email, "password": PASSWORD}).status_code == 422


def test_a_wrong_code_counts_down(client, no_real_email, fresh_email):
    email = fresh_email()
    sign_up(client, email)
    response = client.post("/auth/verify", json={"email": email, "code": "000000"})
    assert response.status_code == 400
    assert "tries left" in response.json()["detail"]


def test_a_code_cannot_be_used_twice(client, no_real_email, fresh_email):
    email = fresh_email()
    sign_up(client, email)
    code = no_real_email.codes[email]

    assert client.post("/auth/verify", json={"email": email, "code": code}).status_code == 200
    again = client.post("/auth/verify", json={"email": email, "code": code})
    assert again.status_code == 400
    assert "already been used" in again.json()["detail"]


def test_you_cannot_sign_in_before_confirming_your_email(client, no_real_email, fresh_email):
    email = fresh_email()
    sign_up(client, email)
    response = client.post("/auth/sign-in", json={"email": email, "password": PASSWORD})
    assert response.status_code == 403


def test_a_wrong_password_does_not_say_which_part_was_wrong(client, no_real_email, fresh_email):
    email = fresh_email()
    sign_up(client, email)
    client.post("/auth/verify", json={"email": email, "code": no_real_email.codes[email]})

    response = client.post("/auth/sign-in", json={"email": email, "password": "not-the-password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "That email or password is wrong."


def test_resend_does_not_reveal_whether_an_email_exists(client, fresh_email):
    response = client.post("/auth/resend-code", json={"email": fresh_email()})
    assert response.status_code == 200
    assert "If that email has an account" in response.json()["message"]


def test_the_session_cookie_is_http_only(client, no_real_email, fresh_email):
    email = fresh_email()
    sign_up(client, email)
    response = client.post("/auth/verify", json={"email": email, "code": no_real_email.codes[email]})
    assert "httponly" in response.headers.get("set-cookie", "").lower()
