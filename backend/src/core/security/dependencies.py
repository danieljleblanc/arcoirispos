import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.models import UserOrgRole
from src.core.security.roles import UserRole
from src.core.security.auth import get_current_user


async def require_admin(
    org_id: uuid.UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Ensures the current user has admin or manager role
    inside the requested organization.
    """

    # Fetch the user's role for this org
    result = await session.execute(
        select(UserOrgRole.role)
        .where(UserOrgRole.user_id == current_user.user_id)
        .where(UserOrgRole.org_id == org_id)
    )
    role = result.scalar_one_or_none()

    if role not in [UserRole.admin.value, UserRole.manager.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager role required",
        )

    return current_user
