# backend/src/core/security/dependencies.py

import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.models import UserOrgRole
from src.core.security.roles import Role
from src.core.security.auth import get_current_user


async def require_any_staff(
    org_id: uuid.UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Ensure the current user belongs to this org (any role except viewer).
    """

    result = await session.execute(
        select(UserOrgRole.role)
        .where(UserOrgRole.user_id == current_user.user_id)
        .where(UserOrgRole.org_id == org_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of this organization",
        )

    return current_user


async def require_admin(
    org_id: uuid.UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Requires owner/admin/manager role in this org.
    """

    result = await session.execute(
        select(UserOrgRole.role)
        .where(UserOrgRole.user_id == current_user.user_id)
        .where(UserOrgRole.org_id == org_id)
    )
    role = result.scalar_one_or_none()

    if role not in [Role.OWNER.value, Role.ADMIN.value, Role.MANAGER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager role required",
        )

    return current_user


async def require_owner(
    org_id: uuid.UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Requires owner role.
    """

    result = await session.execute(
        select(UserOrgRole.role)
        .where(UserOrgRole.user_id == current_user.user_id)
        .where(UserOrgRole.org_id == org_id)
    )
    role = result.scalar_one_or_none()

    if role != Role.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )

    return current_user
