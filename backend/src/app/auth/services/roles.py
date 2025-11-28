# backend/src/app/auth/services/roles.py

from __future__ import annotations
from enum import Enum
from fastapi import Depends, HTTPException, status

from src.app.auth.services.org_context import get_current_org
from src.app.org.models.role_models import UserRole


class Role(str, Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    cashier = "cashier"
    viewer = "viewer"

def require_org_role(*allowed_roles: str):
    """
    Usage example:

    @router.get(
        "/admin",
        dependencies=[Depends(require_org_role(UserRole.owner, UserRole.admin))]
    )

    NOTE:
    - UserRole.<role> already returns the correct lowercase string.
    - allowed_roles is a tuple of role strings such as ("owner", "admin").
    """

    async def verify_role(org_ctx = Depends(get_current_org)):
        # Defensive guard
        if not org_ctx or "role" not in org_ctx:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Organization context is missing or invalid",
            )

        role = org_ctx["role"]

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient organization role. Allowed: {allowed_roles}",
            )

        return True

    return verify_role
