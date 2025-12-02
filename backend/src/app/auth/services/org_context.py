# backend/src/app/auth/services/org_context.py

from fastapi import Depends, Header, HTTPException, status
from uuid import UUID

from src.app.auth.services.auth import get_current_user
from src.app.org.models.organization_models import Organization


async def get_current_org(
    current_user = Depends(get_current_user),
    x_org_id: UUID | None = Header(None, alias="X-Org-ID"),
):
    """
    Temporary working OrgContext:
    - Reads X-Org-ID correctly
    - Returns minimal org context
    """
    if x_org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Org-ID header is required",
        )

    # Synthetic org (only for placeholder)
    fake_org = Organization(
        org_id=x_org_id,
        name="TEMP_ORG",
        legal_name=None,
        display_name=None,
        is_active=True,
        created_at=None,
        updated_at=None,
    )

    return {
        "org_id": x_org_id,
        "org": fake_org,
        "role": "admin",  # placeholder for RBAC
    }
