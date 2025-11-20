# backend/src/services/core/auth_service.py

from typing import Optional, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.core.user_models import User
from src.services.core.repositories.user_repository import get_user_by_email
from src.core.security.hashing import verify_password
from src.core.security.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Core authentication logic:
    - normalize email
    - fetch user
    - enforce is_active
    - verify password

    Returns:
        User instance if authentication succeeds, otherwise None.
    """
    normalized_email = email.strip().lower()
    user = await get_user_by_email(session, normalized_email)

    if not user:
        return None

    if not user.is_active:
        # For security, we simply treat inactive users as failed auth.
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_tokens_for_user(user: User) -> Dict[str, object]:
    """
    Create a standard token payload for a successfully authenticated user.
    This will be the response body for /auth/login.
    """
    user_id_str = str(user.user_id)

    access_token = create_access_token(user_id_str)
    refresh_token = create_refresh_token(user_id_str)

    return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer",
    "user_id": str(user.user_id),
    "display_name": user.display_name,
}


def refresh_access_token(raw_refresh_token: str) -> Optional[Dict[str, object]]:
    """
    Decode a refresh token and produce a new access token.

    Returns:
        dict with new access token if valid, otherwise None.

    NOTE: By design (matching your previous implementation), this does not
    perform a database lookup. That can be tightened later in Option C.
    """
    decoded = decode_token(raw_refresh_token)
    if not decoded:
        return None

    user_id = decoded.get("sub")
    if not user_id:
        return None

    new_access = create_access_token(user_id)

    return {
        "access_token": new_access,
        "token_type": "bearer",
        "user_id": str(user_id),
    }
