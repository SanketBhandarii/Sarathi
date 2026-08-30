from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

CODE_LENGTH = 6
VALID_FOR = timedelta(minutes=10)
MAX_ATTEMPTS = 5
RESEND_GAP = timedelta(seconds=60)


def new_code() -> str:
    return f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"


def fingerprint(code: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{code}".encode()).hexdigest()


def matches(code: str, salt: str, stored: str) -> bool:
    return hmac.compare_digest(fingerprint(code, salt), stored)


def expires_at(now: datetime | None = None) -> datetime:
    return (now or datetime.now(timezone.utc)) + VALID_FOR


def is_expired(deadline: datetime, now: datetime | None = None) -> bool:
    moment = now or datetime.now(timezone.utc)
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return moment > deadline


def can_resend(last_sent: datetime | None, now: datetime | None = None) -> bool:
    if last_sent is None:
        return True
    moment = now or datetime.now(timezone.utc)
    if last_sent.tzinfo is None:
        last_sent = last_sent.replace(tzinfo=timezone.utc)
    return moment - last_sent >= RESEND_GAP
