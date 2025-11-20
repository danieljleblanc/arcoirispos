# src/core/security/schemas.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------
# AUTH REQUEST MODELS
# ---------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: Optional[str] = None
    org_name: str = Field(default="My Organization")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------
# AUTH RESPONSE MODELS
# ---------------------------------------------------------

class UserRead(BaseModel):
    user_id: UUID
    email: EmailStr
    display_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True  # Pydantic v2 equivalent to orm_mode=True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    user: UserRead
    tokens: TokenPair
