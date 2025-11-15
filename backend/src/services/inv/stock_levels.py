# backend/src/services/inv/stock_levels.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StockLevel
from src.services.base_repository import BaseRepository


class StockLevelService(BaseRepository[StockLevel]):
    def __init__(self) -> None:
        super().__init__(StockLevel)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StockLevel]:
        stmt = (
            select(StockLevel)
            .where(StockLevel.org_id == org_id)
            .order_by(StockLevel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        stock_level_id: UUID,
    ) -> Optional[StockLevel]:
        stmt = select(StockLevel).where(StockLevel.stock_level_id == stock_level_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


stock_level_service = StockLevelService()
