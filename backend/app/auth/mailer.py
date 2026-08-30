from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Protocol

from app.core.config import get_settings
from app.language.phrases import Language

SUBJECT = {
    Language.ENGLISH: "Your Sarathi code",
    Language.HINDI: "आपका Sarathi कोड",
}

BODY = {
    Language.ENGLISH: (
        "Your code is {code}\n\n"
        "Type it into Sarathi to confirm your email. It works for 10 minutes.\n\n"
        "If you did not ask for this, you can ignore this email.\n"
    ),
    Language.HINDI: (
        "आपका कोड है {code}\n\n"
        "अपना ईमेल पक्का करने के लिए इसे Sarathi में लिखें। यह 10 मिनट तक चलेगा।\n\n"
        "अगर आपने यह नहीं माँगा था, तो इस ईमेल को छोड़ दें।\n"
    ),
}


class Mailer(Protocol):
    def send_code(self, to: str, code: str, language: Language) -> None: ...


class ConsoleMailer:
    def __init__(self, log_path: Path | None = None) -> None:
        self.log_path = log_path

    def send_code(self, to: str, code: str, language: Language = Language.ENGLISH) -> None:
        line = f"to {to}: {SUBJECT[language]} -> {code}"
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")


class SmtpMailer:
    def __init__(
        self, host: str, port: int, username: str, password: str, sender: str, use_tls: bool = True
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender
        self.use_tls = use_tls

    def send_code(self, to: str, code: str, language: Language = Language.ENGLISH) -> None:
        message = EmailMessage()
        message["Subject"] = SUBJECT[language]
        message["From"] = self.sender
        message["To"] = to
        message.set_content(BODY[language].format(code=code))

        context = ssl.create_default_context()
        if self.port == 465:
            with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=30) as server:
                server.login(self.username, self.password)
                server.send_message(message)
            return

        with smtplib.SMTP(self.host, self.port, timeout=30) as server:
            if self.use_tls:
                server.starttls(context=context)
            server.login(self.username, self.password)
            server.send_message(message)


def get_mailer() -> Mailer:
    settings = get_settings()
    if settings.smtp_host and settings.smtp_username and settings.smtp_password:
        return SmtpMailer(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            sender=settings.smtp_from or settings.smtp_username,
        )
    return ConsoleMailer(log_path=settings.notifications_path.parent / "emails.log")
