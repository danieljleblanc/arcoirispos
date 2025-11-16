from fastapi import Depends, HTTPException, status
from typing import List

from src.core.security.auth import get_current_user
from src.services.core.roles import role_service  # we add this next


def require_roles(allowed_roles: List[str]):
    async def wrapper(
        current_user = Depends(get_current_user),
    ):
        user_roles = await role_service.get_roles_for_user(
            user_id=current_user.user_id
        )

        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return wrapper
