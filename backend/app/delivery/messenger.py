from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from app.core.config import get_settings
from app.language.phrases import Language


class OutgoingMessage(BaseModel):
    to: str
    body: str
    language: Language = Language.ENGLISH


class SentMessage(BaseModel):
    to: str
    body: str
    channel: str
    sent_at: datetime
    reference: str | None = None


class Messenger(Protocol):
    channel: str

    def send(self, message: OutgoingMessage) -> SentMessage: ...


class ConsoleMessenger:
    channel = "console"

    def __init__(self, log_path: Path | None = None) -> None:
        self.log_path = log_path

    def send(self, message: OutgoingMessage) -> SentMessage:
        line = f"[{message.language.value}] to {message.to}: {message.body}"
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        return SentMessage(
            to=message.to,
            body=message.body,
            channel=self.channel,
            sent_at=datetime.now(timezone.utc),
        )


class WhatsAppMessenger:
    channel = "whatsapp"

    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        from twilio.rest import Client

        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send(self, message: OutgoingMessage) -> SentMessage:
        sent = self.client.messages.create(
            from_=f"whatsapp:{self.from_number}",
            to=f"whatsapp:{message.to}",
            body=message.body,
        )
        return SentMessage(
            to=message.to,
            body=message.body,
            channel=self.channel,
            sent_at=datetime.now(timezone.utc),
            reference=sent.sid,
        )


def get_messenger() -> Messenger:
    settings = get_settings()
    if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_whatsapp_from:
        return WhatsAppMessenger(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
            settings.twilio_whatsapp_from,
        )
    return ConsoleMessenger(log_path=settings.notifications_path.parent / "messages.log")
