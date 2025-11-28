# backend/src/app/auth/services/permissions.py

from __future__ import annotations

from typing import List
from fastapi import Depends, HTTPException, status

# Local import: safe & stable
from src.app.auth.services.auth import get_current_user


# -----------------------------------------------------
# REQUIRE AUTHENTICATED USER
# -----------------------------------------------------
async def require_user(user = Depends(get_current_user)):
    """
    Allows any authenticated user.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user


# -----------------------------------------------------
# REQUIRE USER WITH SPECIFIC ROLE(S)
# -----------------------------------------------------
def require_roles(roles: List[str]):
    """
    Dependency factory enforcing at least one required role.
    Assumes the User object has `roles` attribute, but fails safely.
    """

    async def role_checker(user = Depends(get_current_user)):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # If missing, default to empty list instead of raising AttributeError
        user_roles = getattr(user, "roles", []) or []

        # Enforce at least one match
        if not any(role in user_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {roles}",
            )

        return user

    return role_checker
