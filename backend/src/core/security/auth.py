# backend/src/core/security/auth.py

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.core.user_models import User
from src.core.security.jwt_utils import decode_token
from src.services.core.repositories.user_repository import get_user_by_id


# This is used by FastAPI's dependency system and the OpenAPI schema.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Resolve the current user from a Bearer token.

    - Decodes the JWT
    - Extracts the 'sub' claim as user_id
    - Loads the user from the database
    - Ensures the user is active

    Raises HTTP 401 on any failure.
    """
    payload: Optional[dict] = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_uuid = uuid.UUID(user_id_raw)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    user = await get_user_by_id(session, user_uuid)

    if not user or not user.is_active:
        # Purposefully generic to avoid leaking which part failed.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User disabled or not found",
        )

    return user
