# backend/src/app/org/repositories/org_repository.py

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.org.models.organization_models import Organization


async def get_org_by_id(session: AsyncSession, org_id: UUID) -> Organization | None:
    stmt = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_org_by_name(session: AsyncSession, name: str) -> Organization | None:
    stmt = select(Organization).where(Organization.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
