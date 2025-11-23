# src/core/security/dependencies.py

from fastapi import Depends, HTTPException, status

from src.core.security.auth import get_current_user
from src.core.security.org_context import get_current_org
from src.core.security.roles import Role


# =====================================================================
# RBAC helpers bound to *current org* (Option B1)
# ---------------------------------------------------------------------
# These assume:
# - get_current_org() already validated org + membership
# - we only need to check "how powerful" the role is
# =====================================================================


async def require_any_staff_org(
    org_ctx=Depends(get_current_org),
    current_user=Depends(get_current_user),
):
    """
    Allow any STAFF-style role within the active org:

    Allowed:
      - owner
      - admin
      - manager
      - cashier
      - support   (if you choose to define this)
    Blocked:
      - viewer

    Returns the current_user for convenience.
    """

    role = org_ctx["role"]

    if role == Role.VIEWER.value:
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
    Require an administrative role for this org:

    Allowed:
      - owner
      - admin
      - manager

    Blocked:
      - cashier
      - support
      - viewer
    """

    role = org_ctx["role"]

    if role not in (Role.OWNER.value, Role.ADMIN.value, Role.MANAGER.value):
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
    Require OWNER for very sensitive actions (billing, deleting org, etc).
    """

    role = org_ctx["role"]

    if role != Role.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )

    return current_user
