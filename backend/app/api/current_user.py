from __future__ import annotations

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth import tokens
from app.db.models import User

SESSION_COOKIE = "sarathi_session"


def _token_from(authorization: str | None, cookie: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return cookie


def current_user(
    authorization: str | None = Header(default=None),
    sarathi_session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _token_from(authorization, sarathi_session)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in first."
        )
    try:
        user_id, _ = tokens.read(token)
    except tokens.BadToken as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    user = db.get(User, user_id)
    if user is None or not user.is_verified:
        raise HTTPException(status_code=401, detail="Please sign in first.")
    return user
