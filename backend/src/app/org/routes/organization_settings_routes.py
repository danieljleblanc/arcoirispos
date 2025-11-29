# backend/src/app/org/routes/organization_settings_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_async_session
from src.app.auth.services.dependencies import get_current_user
from src.app.org.services.organization_settings_service import (
    get_or_create_org_settings,
    update_org_settings_service,
)
from src.app.org.schemas.organization_settings_schema import (
    OrganizationSettingsRead,
    OrganizationSettingsUpdate,
)


router = APIRouter(
    prefix="/org/settings",
    tags=["Organization Settings"],
)


# ---------------------------------------------------------
# GET /org/settings  → fetch settings for user's org
# ---------------------------------------------------------
@router.get("/", response_model=OrganizationSettingsRead)
async def get_settings(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """
    Returns settings for the authenticated user's active organization.
    """

    # TODO: Replace once you support multi-org selection
    org_id: UUID = current_user.active_org_id

    settings = await get_or_create_org_settings(session, org_id)
    return settings


# ---------------------------------------------------------
# PUT /org/settings  → update settings for user's org
# ---------------------------------------------------------
@router.put("/", response_model=OrganizationSettingsRead)
async def update_settings(
    payload: OrganizationSettingsUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """
    Allows an org admin to update rounding, inventory modes, and other behavior.
    """

    # TODO: Role enforcement (owner/admin only)
    # if current_user.role not in ["owner", "admin"]:
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")

    org_id: UUID = current_user.active_org_id

    updated = await update_org_settings_service(session, org_id, payload)
    return updated
