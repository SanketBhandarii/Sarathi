from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import otp
from app.auth.mailer import Mailer, get_mailer
from app.auth.passwords import hash_password, verify_password
from app.db.models import EmailCode, User
from app.language.phrases import Language

LOCK_AFTER = 6


class AuthProblem(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


def normalise_email(email: str) -> str:
    return email.strip().lower()


def find_user(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == normalise_email(email)))


def _latest_code(session: Session, user_id: int, purpose: str) -> EmailCode | None:
    return session.scalar(
        select(EmailCode)
        .where(EmailCode.user_id == user_id, EmailCode.purpose == purpose)
        .order_by(EmailCode.sent_at.desc())
        .limit(1)
    )


def issue_code(
    session: Session,
    user: User,
    purpose: str = "verify_email",
    mailer: Mailer | None = None,
    language: Language = Language.ENGLISH,
) -> EmailCode:
    previous = _latest_code(session, user.id, purpose)
    if previous and not otp.can_resend(previous.sent_at):
        raise AuthProblem("Please wait a minute before asking for another code.", 429)

    code = otp.new_code()
    record = EmailCode(
        user_id=user.id,
        purpose=purpose,
        code_hash=otp.fingerprint(code, str(user.id)),
        expires_at=otp.expires_at(),
    )
    session.add(record)
    session.flush()

    (mailer or get_mailer()).send_code(user.email, code, language)
    return record


def register(
    session: Session,
    email: str,
    password: str,
    mailer: Mailer | None = None,
    language: Language = Language.ENGLISH,
) -> User:
    address = normalise_email(email)
    existing = find_user(session, address)
    if existing and existing.is_verified:
        raise AuthProblem("An account with this email already exists. Try signing in.", 409)

    if existing:
        existing.password_hash = hash_password(password)
        user = existing
    else:
        user = User(email=address, password_hash=hash_password(password))
        session.add(user)
    session.flush()

    issue_code(session, user, mailer=mailer, language=language)
    return user


def verify_code(session: Session, email: str, code: str, purpose: str = "verify_email") -> User:
    user = find_user(session, email)
    if user is None:
        raise AuthProblem("We could not find that email.", 404)

    record = _latest_code(session, user.id, purpose)
    if record is None:
        raise AuthProblem("Ask for a code first.", 400)
    if record.used_at is not None:
        raise AuthProblem("That code has already been used. Ask for a new one.", 400)
    if otp.is_expired(record.expires_at):
        raise AuthProblem("That code has expired. Ask for a new one.", 400)
    if record.attempts >= otp.MAX_ATTEMPTS:
        raise AuthProblem("Too many wrong tries. Ask for a new code.", 429)

    if not otp.matches(code, str(user.id), record.code_hash):
        record.attempts += 1
        session.flush()
        left = otp.MAX_ATTEMPTS - record.attempts
        raise AuthProblem(f"That code is wrong. You have {max(0, left)} tries left.", 400)

    record.used_at = datetime.now(timezone.utc)
    user.is_verified = True
    user.verified_at = datetime.now(timezone.utc)
    session.flush()
    return user


def sign_in(session: Session, email: str, password: str) -> User:
    user = find_user(session, email)
    if user is None:
        raise AuthProblem("That email or password is wrong.", 401)

    now = datetime.now(timezone.utc)
    if user.locked_until is not None:
        locked = user.locked_until
        if locked.tzinfo is None:
            locked = locked.replace(tzinfo=timezone.utc)
        if locked > now:
            raise AuthProblem("Too many wrong tries. Please try again later.", 429)

    if not verify_password(password, user.password_hash):
        user.failed_logins += 1
        if user.failed_logins >= LOCK_AFTER:
            from datetime import timedelta

            user.locked_until = now + timedelta(minutes=15)
        session.flush()
        raise AuthProblem("That email or password is wrong.", 401)

    if not user.is_verified:
        raise AuthProblem("Please confirm your email first.", 403)

    user.failed_logins = 0
    user.locked_until = None
    session.flush()
    return user
