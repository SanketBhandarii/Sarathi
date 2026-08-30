from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"
ISSUER = "sarathi"


class BadToken(ValueError):
    pass


def issue(user_id: int, email: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iss": ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.session_hours)).timestamp()),
    }
    return jwt.encode(payload, settings.session_secret, algorithm=ALGORITHM)


def read(token: str) -> tuple[int, str]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.session_secret, algorithms=[ALGORITHM], issuer=ISSUER
        )
    except jwt.ExpiredSignatureError as error:
        raise BadToken("your session has expired, please sign in again") from error
    except jwt.PyJWTError as error:
        raise BadToken("this session is not valid") from error

    subject = payload.get("sub")
    email = payload.get("email")
    if not subject or not email:
        raise BadToken("this session is not valid")
    return int(subject), str(email)
