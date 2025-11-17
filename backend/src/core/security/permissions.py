# backend/src/core/security/permissions.py

from fastapi import Depends, HTTPException, status
from typing import List

from src.core.security.auth import get_current_user


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
    Dependency factory:
    Returns a function that enforces at least one required role.
    """

    async def role_checker(user = Depends(get_current_user)):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # user.roles is a list of role strings provided by auth.py
        user_roles = getattr(user, "roles", [])

        if not any(r in user_roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {roles}",
            )

        return user

    return role_checker
