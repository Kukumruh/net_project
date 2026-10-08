import os
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")


def get_secret():
    secret = os.getenv("SECRET_KEY", "")
    if len(secret) < 32:
        raise RuntimeError("SECRET_KEY должен содержать минимум 32 символа")
    return secret


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return password_hash.verify(password, encoded)
    except (ValueError, UnknownHashError):
        # Legacy demo hashes are deliberately not accepted as credentials.
        password_hash.verify(password, DUMMY_HASH)
        return False


def create_token(user_id: int):
    now = datetime.now(UTC)
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=30)},
        get_secret(),
        algorithm="HS256",
    )
