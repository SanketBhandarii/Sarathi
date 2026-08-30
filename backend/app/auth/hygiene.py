from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User

UNVERIFIED_LIFETIME = timedelta(hours=24)

THROWAWAY_DOMAINS = {
    "example.com", "example.org", "example.net", "test.com", "test.test",
    "mailinator.com", "yopmail.com", "guerrillamail.com", "10minutemail.com",
    "tempmail.com", "temp-mail.org", "trashmail.com", "sharklasers.com",
    "getnada.com", "dispostable.com", "fakeinbox.com", "throwawaymail.com",
    "maildrop.cc", "mailnesia.com", "spam4.me", "grr.la",
}

SHAPE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,24}$", re.IGNORECASE)


class EmailJudgement(BaseModel):
    email: str
    looks_real: bool
    reason: str


def domain_of(email: str) -> str:
    return email.rsplit("@", 1)[-1].strip().lower()


@lru_cache(maxsize=512)
def domain_accepts_mail(domain: str) -> bool:
    try:
        import dns.resolver

        answers = dns.resolver.resolve(domain, "MX", lifetime=6)
        return len(answers) > 0
    except Exception:
        return False


def judge(email: str, check_dns: bool = True) -> EmailJudgement:
    address = email.strip().lower()

    if not SHAPE.match(address):
        return EmailJudgement(email=address, looks_real=False, reason="that is not a real email address")

    domain = domain_of(address)
    if domain in THROWAWAY_DOMAINS:
        return EmailJudgement(
            email=address, looks_real=False, reason="throwaway email addresses are not accepted"
        )

    if check_dns and not domain_accepts_mail(domain):
        return EmailJudgement(
            email=address, looks_real=False, reason=f"{domain} does not receive email"
        )

    return EmailJudgement(email=address, looks_real=True, reason="looks fine")


class Sweep(BaseModel):
    expired_unverified: list[str] = []
    throwaway: list[str] = []
    undeliverable: list[str] = []

    @property
    def total(self) -> int:
        return len(self.expired_unverified) + len(self.throwaway) + len(self.undeliverable)


def sweep_users(session: Session, now: datetime | None = None, check_dns: bool = True) -> Sweep:
    moment = now or datetime.now(timezone.utc)
    cutoff = moment - UNVERIFIED_LIFETIME
    report = Sweep()

    for user in session.scalars(select(User).where(User.is_verified.is_(False))).all():
        created = user.created_at
        if created is not None and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        verdict = judge(user.email, check_dns=check_dns)
        if not verdict.looks_real:
            bucket = (
                report.throwaway
                if "throwaway" in verdict.reason
                else report.undeliverable
            )
            bucket.append(user.email)
            session.delete(user)
            continue

        if created is not None and created < cutoff:
            report.expired_unverified.append(user.email)
            session.delete(user)

    session.flush()
    return report
