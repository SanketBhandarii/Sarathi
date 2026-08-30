from __future__ import annotations

import random

import pytest

from app.auth import service as auth_service
from app.language.phrases import Language


class CapturingMailer:
    def __init__(self) -> None:
        self.codes: dict[str, str] = {}

    def send_code(self, to: str, code: str, language: Language = Language.ENGLISH) -> None:
        self.codes[to.strip().lower()] = code


@pytest.fixture(autouse=True)
def no_real_email(monkeypatch):
    mailer = CapturingMailer()
    monkeypatch.setattr(auth_service, "get_mailer", lambda: mailer)
    return mailer


@pytest.fixture
def fresh_email():
    def make() -> str:
        return f"sarathi.test.{random.randint(100000, 999999)}@gmail.com"

    return make
