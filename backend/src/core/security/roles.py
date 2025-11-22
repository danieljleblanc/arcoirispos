from enum import Enum
from fastapi import Depends, HTTPException, status
from src.core.security.org_context import get_current_org

class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

def require_org_role(*allowed_roles):
    """
    Dependency factory:
    @router.get(..., dependencies=[Depends(require_org_role("owner", "admin"))])
    """
    async def verify_role(org_ctx=Depends(get_current_org)):
        if org_ctx["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient organization role",
            )
        return True

    return verify_role