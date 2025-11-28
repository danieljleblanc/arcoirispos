# backend/src/app/auth/services/dependencies.py

from fastapi import Depends, HTTPException, status

# ✅ Correct import location for user auth
from src.app.auth.services.auth import get_current_user

# ✅ Correct org context import
from src.app.auth.services.org_context import get_current_org

# ✅ Correct Role Enum import
from src.app.org.models.role_models import UserRole as Role


# =====================================================================
# RBAC helpers bound to *current org*
# =====================================================================

async def require_any_staff_org(
    org_ctx=Depends(get_current_org),
    current_user=Depends(get_current_user),
):
    """
    Allow any STAFF-style role within the active org:
      owner, admin, manager, cashier, support
    Block: viewer
    """
    role = org_ctx["role"]

    if role == Role.viewer.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role (viewer cannot perform staff operations)",
        )

    return current_user


async def require_admin_org(
    org_ctx=Depends(get_current_org),
    current_user=Depends(get_current_user),
):
    """
    Require: owner, admin, manager
    """
    role = org_ctx["role"]

    if role not in (
        Role.owner.value,
        Role.admin.value,
        Role.manager.value,
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
    Require OWNER for sensitive operations.
    """
    role = org_ctx["role"]

    if role != Role.owner.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )

    return current_user