# backend/src/app/org/repositories/organization_settings_repository.py

from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.org.models.organization_settings_model import OrganizationSettings
from src.app.org.schemas.organization_settings_schema import (
    OrganizationSettingsUpdate,
    OrganizationSettingsCreate,
)


# ---------------------------------------------------------
# CREATE default settings when a new organization is created
# ---------------------------------------------------------
async def create_default_settings(
    session: AsyncSession,
    org_id: UUID,
    payload: OrganizationSettingsCreate | None = None,
) -> OrganizationSettings:

    data = payload.dict() if payload else {}

    settings = OrganizationSettings(
        org_id=org_id,
        **data,
    )

    session.add(settings)
    await session.flush()  # ensures settings_id is generated
    return settings


# ---------------------------------------------------------
# READ settings for an org
# ---------------------------------------------------------
async def get_settings_by_org_id(
    session: AsyncSession,
    org_id: UUID,
) -> OrganizationSettings | None:

    stmt = select(OrganizationSettings).where(OrganizationSettings.org_id == org_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# ---------------------------------------------------------
# UPDATE settings
# ---------------------------------------------------------
async def update_settings(
    session: AsyncSession,
    org_id: UUID,
    payload: OrganizationSettingsUpdate,
) -> OrganizationSettings | None:

    stmt = (
        update(OrganizationSettings)
        .where(OrganizationSettings.org_id == org_id)
        .values(**payload.dict(exclude_unset=True))
        .returning(OrganizationSettings)
    )

    result = await session.execute(stmt)
    updated = result.scalar_one_or_none()

    return updated


# ---------------------------------------------------------
# ENSURE organization has settings (auto-create if missing)
# ---------------------------------------------------------
async def ensure_settings_exist(
    session: AsyncSession,
    org_id: UUID,
) -> OrganizationSettings:

    existing = await get_settings_by_org_id(session, org_id)

    if existing:
        return existing

    # If not found, create default settings
    default_settings = OrganizationSettingsCreate()
    return await create_default_settings(session, org_id, default_settings)
