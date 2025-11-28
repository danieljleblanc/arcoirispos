# backend/src/app/auth/services/jwt_utils.py

import jwt
from datetime import datetime, timedelta
from typing import Optional

from src.app.core.config import settings


# Token lifetime settings (moved here cleanly)
ACCESS_TOKEN_EXPIRE_MINUTES = 60          # override if needed
REFRESH_TOKEN_EXPIRE_DAYS = 30
JWT_ALGORITHM = "HS256"


def _create_token(user_id: str, expires_delta: timedelta) -> str:
    """
    Internal helper to create a signed JWT.
    """
    now = datetime.utcnow()
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        user_id,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
