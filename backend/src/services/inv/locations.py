# backend/src/services/inv/locations.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Location
from src.services.base_repository import BaseRepository


class LocationService(BaseRepository[Location]):
    def __init__(self) -> None:
        super().__init__(Location)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Location]:
        stmt = (
            select(Location)
            .where(
                Location.org_id == org_id,
                Location.deleted_at.is_(None),   # soft delete filter
            )
            .order_by(Location.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        location_id: UUID,
    ) -> Optional[Location]:
        stmt = (
            select(Location)
            .where(
                Location.location_id == location_id,
                Location.deleted_at.is_(None),   # soft delete filter
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_location(
        self,
        session: AsyncSession,
        location_id: UUID,
    ) -> Optional[Location]:
        """
        Soft-delete using BaseRepository logic.
        """
        return await self.delete(session, location_id)


location_service = LocationService()
