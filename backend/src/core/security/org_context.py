# src/core/security/org_context.py

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.core.database import get_session
from src.core.security.auth import get_current_user
from src.models.core.organization_models import Organization
from src.models.core.role_models import UserOrgRole


async def get_current_org(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
    x_org_id: str | None = Header(default=None, alias="X-Org-ID"),
):
    """
    Determines the acting organization for a request.

    Priority:
    1. Use X-Org-ID header if supplied
    2. Fallback to user's primary org (in the future)

    Validates:
    - Org exists
    - User is a member of that org
    """

    if not x_org_id:
        # FUTURE: auto-select primary org
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Org-ID header required",
        )

    try:
        org_uuid = UUID(x_org_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid X-Org-ID format (must be UUID)",
        )

    # 1. Verify org exists
    org_result = await session.execute(
        select(Organization).where(Organization.org_id == org_uuid)
    )
    org = org_result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    # 2. Verify user belongs to org
    role_result = await session.execute(
        select(UserOrgRole).where(
            UserOrgRole.org_id == org_uuid,
            UserOrgRole.user_id == current_user.user_id,
        )
    )
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=403,
            detail="User does not belong to this organization",
        )

    # Return a simple context object
    return {
        "org": org,
        "role": role.role,        # "owner", "admin", "cashier", etc.
        "is_primary": role.is_primary,
    }
