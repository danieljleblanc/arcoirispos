# backend/src/app/org/services/auth_service.py

from typing import Optional, Dict

from sqlalchemy.ext.asyncio import AsyncSession

# FIXED IMPORT – correct path to models
from src.app.org.models.user_models import User

# FIXED IMPORT VALIDATION – correct root namespace
from src.app.org.repositories.user_repository import get_user_by_email

from src.app.auth.services.hashing import verify_password
from src.app.auth.services.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


# ---------------------------------------------------------
# AUTHENTICATION LOGIC
# ---------------------------------------------------------
async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate user by email + password.
    """
    normalized_email = email.strip().lower()
    user = await get_user_by_email(session, normalized_email)

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


# ---------------------------------------------------------
# TOKEN CREATION
# ---------------------------------------------------------
def create_tokens_for_user(user: User) -> Dict[str, object]:
    user_id_str = str(user.user_id)

    access_token = create_access_token(user_id_str)
    refresh_token = create_refresh_token(user_id_str)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user_id_str,
        "display_name": user.display_name,
    }


# ---------------------------------------------------------
# REFRESH TOKEN
# ---------------------------------------------------------
def refresh_access_token(raw_refresh_token: str) -> Optional[Dict[str, object]]:
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
