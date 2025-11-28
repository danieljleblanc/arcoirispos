# backend/src/app/auth/services/security.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

from src.app.core.config import settings


# ---------------------------------------------------------
# CONSTANTS & JWT SETTINGS
# ---------------------------------------------------------

ALGORITHM = "HS256"
JWT_ALGORITHM = ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a bcrypt password."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------
# TOKEN CREATION HELPERS
# ---------------------------------------------------------

def _create_token(
    subject: str,
    token_type: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Internal JWT generator.
    Includes subject, token type, issued time, and expiration.
    """
    now = datetime.now(timezone.utc)

    # Default expiry handling
    if expires_delta is None:
        if token_type == "access":
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == "refresh":
            expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = now + expires_delta

    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(subject, "access", expires_delta)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(subject, "refresh", expires_delta)


# ---------------------------------------------------------
# TOKEN DECODING
# ---------------------------------------------------------

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT and return its payload.

    Raises ValueError on any failure (invalid signature, expiry, etc.).
    """
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    except PyJWTError as exc:
        raise ValueError("Invalid token") from exc
