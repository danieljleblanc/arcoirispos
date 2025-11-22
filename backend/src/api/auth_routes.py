from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.core.database import get_session
from src.services.core.auth_service import (
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
    Authenticate a user and return a token pair.

    Notes:
    - Does NOT require org context (users may belong to multiple orgs).
    - Email normalization handled inside authenticate_user().
    """
    user = await authenticate_user(session, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Tokens include user_id; org selection comes later on workflows that require it.
    return create_tokens_for_user(user)


# ---------------------------------------------------------
# REFRESH ACCESS TOKEN
# ---------------------------------------------------------
@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token_endpoint(payload: RefreshRequest):
    """
    Exchange a refresh token for a new access token.

    NOTE:
    - Matches your legacy behavior (no DB lookup).
    - In Phase 3 we can add DB-validated refresh tokens, rotation, revocation, etc.
    """
    data = refresh_access_token(payload.refresh_token)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return data
