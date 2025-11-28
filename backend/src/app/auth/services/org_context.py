# src/app/auth/services/org_context.py

from __future__ import annotations

from fastapi import Depends
from uuid import UUID

# These imports are valid and match your directory layout
from src.app.org.models.user_models import User
from src.app.org.models.organization_models import Organization


async def get_current_org(
    user: User = Depends(),
):
    """
    Temporary safe placeholder implementation.

    Until real organization resolution logic is rebuilt, this
    returns a minimal synthetic org context object shaped exactly
    like the real one so downstream dependencies do not break.

    Real version will:
        - Read X-Org-ID header
        - Verify membership via UserOrgRole table
        - Attach role and org to context
    """

    # Minimal synthetic object with required structure.
    # Enough for routes and permission checks not to explode.

    fake_org = Organization(
        org_id=UUID("00000000-0000-0000-0000-000000000000"),
        name="TEMP_ORG",
        legal_name=None,
        display_name=None,
        is_active=True,
        created_at=None,
        updated_at=None,
    )

    return {
        "org": fake_org,
        "role": "admin",  # permissive placeholder until RBAC restored
    }
