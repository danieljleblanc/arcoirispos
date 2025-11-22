import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.core.role_models import UserOrgRole
from src.core.security.roles import Role
from src.core.security.auth import get_current_user


# =====================================================================
# require_any_staff()
# ---------------------------------------------------------------------
# Allows: owner, admin, manager, cashier, support (anything except viewer)
# Ensures: user belongs to org_id and has a valid staff-level role
# =====================================================================
async def require_any_staff(
    org_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Ensure the current user belongs to this org with ANY staff role.
    Disallowed: viewer or missing org membership.
    """

    result = await session.execute(
        select(UserOrgRole.role)
        .where(UserOrgRole.user_id == current_user.user_id)
        .where(UserOrgRole.org_id == org_id)
    )
    role = result.scalar_one_or_none()

    # No membership?
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of this organization",
        )

    # "viewer" cannot perform any staff operations
    if role == Role.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role (viewer)",
        )

    return current_user


# =====================================================================
# require_admin()
# ---------------------------------------------------------------------
# Allows: owner, admin, manager
# Ensures: user belongs to org and is allowed administrative operations
# =====================================================================
async def require_admin(
    org_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Requires owner/admin/manager role in this org.
    Used for CREATE / UPDATE / DELETE operations.
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


# =====================================================================
# require_owner()
# ---------------------------------------------------------------------
# Allows: ONLY org owner
# Ensures: user has full organization control
# =====================================================================
async def require_owner(
    org_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Requires owner role for sensitive organization-wide actions.
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


# =====================================================================
# get_current_org() — kept for future Option C work (NOT used in Option A+)
# ---------------------------------------------------------------------
# Right now we always pass org_id explicitly to routes + RBAC dependencies.
# This placeholder is here only so imports won't break if something still
# references get_current_org. It simply echoes the org_id.
# =====================================================================
async def get_current_org(org_id: uuid.UUID):
    """
    Placeholder for a future, richer OrgContext.

    Currently:
    - Just returns the org_id passed in.
    - Not used by Option A+ routes; org_id is explicit.
    """
    return org_id
