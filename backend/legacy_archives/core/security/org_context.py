# src/core/security/org_context.py

from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.auth.services.auth import get_current_user
from app.org.app.organization_models.models import Organization
from app.org.app.role_models.models import UserOrgRole


async def get_current_org(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
    x_org_id: str | None = Header(default=None, alias="X-Org-ID"),
):
    """
    Resolve the *active organization context* for this request.

    Rules (Option A1/C1):
    - Require X-Org-ID header (UUID string)
    - Validate that org exists in core.organizations
    - Validate that user has a membership in that org in core.user_org_roles

    Returns a simple dict ("A1"):
    {
        "org": Organization ORM instance,
        "role": "<role-name>",        # "owner" | "admin" | "manager" | "cashier" | "viewer" | ...
        "is_primary": bool,
    }
    """

    if not x_org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Org-ID header required",
        )

    try:
        org_uuid = UUID(x_org_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Org-ID format (must be UUID)",
        )

    # 1) Check org exists
    org_result = await session.execute(
        select(Organization).where(Organization.org_id == org_uuid)
    )
    org = org_result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # 2) Check user membership + role
    membership_result = await session.execute(
        select(UserOrgRole).where(
            UserOrgRole.org_id == org_uuid,
            UserOrgRole.user_id == current_user.user_id,
        )
    )
    membership = membership_result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this organization",
        )

    return {
        "org": org,
        "role": membership.role,
        "is_primary": membership.is_primary,
    }
