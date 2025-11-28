# backend/src/app/auth/routes/auth_routes.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.app.core.database import get_session

# ✔ FIXED: correct import path for auth_service
from src.app.org.services.auth_service import (
    authenticate_user,
    create_tokens_for_user,
    refresh_access_token,
)


router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# ---------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    display_name: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login", response_model=TokenPairResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Authenticate user and return token pair.
    """
    user = await authenticate_user(session, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return create_tokens_for_user(user)


# ---------------------------------------------------------
# REFRESH ACCESS TOKEN
# ---------------------------------------------------------
@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token_endpoint(payload: RefreshRequest):
    data = refresh_access_token(payload.refresh_token)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return data
