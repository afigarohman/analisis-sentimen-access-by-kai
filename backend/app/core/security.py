import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))


def hash_password(password: str) -> str:
    """Hash bcrypt via library resmi (hindari crash passlib + bcrypt 4.1+ di Windows)."""
    raw = password.encode("utf-8")
    if len(raw) > 72:
        raw = raw[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12)).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(*, sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": int(expire.timestamp())}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
