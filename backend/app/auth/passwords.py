from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

MIN_LENGTH = 8

_hasher = PasswordHasher()


class WeakPassword(ValueError):
    pass


def check_strength(password: str) -> None:
    if len(password) < MIN_LENGTH:
        raise WeakPassword(f"Your password must be at least {MIN_LENGTH} characters.")
    if password.isdigit():
        raise WeakPassword("Your password cannot be only numbers.")
    if password.lower() in {"password", "12345678", "sarathi123"}:
        raise WeakPassword("That password is too easy to guess.")


def hash_password(password: str) -> str:
    check_strength(password)
    return _hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return _hasher.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(stored_hash)
    except InvalidHashError:
        return True
