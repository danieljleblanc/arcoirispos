# backend/src/api/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pydantic import BaseModel, EmailStr

from src.core.database import get_session
from src.models.models import User
from src.core.security.hashing import verify_password
from src.core.security.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------
# LOGIN REQUEST PAYLOAD
# ---------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    # Ensure email is lowercase for consistent DB matching
    stmt = select(User).where(User.email == payload.email.lower())
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "display_name": user.display_name,
    }


# ---------------------------------------------------------
# REFRESH ACCESS TOKEN
# ---------------------------------------------------------
class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_token_endpoint(
    payload: RefreshRequest,
):
    """
    Allows swapping a valid refresh token for a new access token.
    Does NOT require DB access.
    """
    decoded = decode_token(payload.refresh_token)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token",
        )

    new_access = create_access_token(user_id)

    return {
        "access_token": new_access,
        "token_type": "bearer",
        "user_id": user_id,
    }
