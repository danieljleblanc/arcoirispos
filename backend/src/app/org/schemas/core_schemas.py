# backend/src/app/org/schemas/core_schemas.py

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


# ============================================================
# ORGANIZATION SCHEMAS
# ============================================================

class OrganizationBase(BaseModel):
    name: str
    legal_name: Optional[str] = None
    timezone: str = "UTC"
    base_currency: str = "USD"
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    timezone: Optional[str] = None
    base_currency: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationRead(OrganizationBase):
    org_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   # Pydantic v2 compatible


# ============================================================
# USER SCHEMAS
# ============================================================

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str   # plain-text input; will be hashed by service layer


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# USER-ORG-ROLE SCHEMAS
# ============================================================

class UserOrgRoleBase(BaseModel):
    org_id: UUID
    user_id: UUID
    role: str
    is_primary: bool = False


class UserOrgRoleCreate(UserOrgRoleBase):
    pass


class UserOrgRoleRead(UserOrgRoleBase):
    user_org_role_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
