# backend/src/app/auth/services/dependencies.py

from fastapi import Depends, HTTPException, status

from src.app.auth.services.auth import get_current_user
from src.app.auth.services.org_context import get_current_org
from src.app.org.models.role_models import UserRole as Role


# =====================================================================
# RBAC bound to current org
# =====================================================================


async def require_any_staff_org(
    org_ctx=Depends(get_current_org),
    current_user=Depends(get_current_user),
):
    """
    Allow any STAFF role in the active org:
      owner, admin, manager, cashier, support
    Block viewer.
    """
    role = org_ctx["role"]

    if role == Role.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewer role cannot perform staff operations",
        )

    return current_user


async def require_admin_org(
    org_ctx=Depends(get_current_org),
    current_user=Depends(get_current_user),
):
    """
    Require admin-level roles:
      owner, admin, manager
    """
    role = org_ctx["role"]

    if role not in (
        Role.OWNER.value,
        Role.ADMIN.value,
        Role.MANAGER.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin/Manager/Owner role required",
        )

    return current_user


async def require_owner_org(
    org_ctx=Depends(get_current_org),
    current_user=Depends(get_current_user),
):
    """
    Require OWNER for the current org.
    """
    role = org_ctx["role"]

    if role != Role.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )

    return current_user
