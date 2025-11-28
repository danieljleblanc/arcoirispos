# backend/src/app/inventory/services/stock_levels.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.inventory.models.stock_level_models import StockLevel
from src.app.core.base_repository import BaseRepository


class StockLevelService(BaseRepository[StockLevel]):
    def __init__(self) -> None:
        super().__init__(StockLevel)

    # ---------------------------------------------------------
    # LIST STOCK LEVELS BY ORG
    # ---------------------------------------------------------
    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StockLevel]:

        stmt = (
            select(StockLevel)
            .where(
                StockLevel.org_id == org_id,
                StockLevel.deleted_at.is_(None),
            )
            .order_by(StockLevel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    # ---------------------------------------------------------
    # GET SINGLE STOCK LEVEL
    # ---------------------------------------------------------
    async def get_by_id(
        self,
        session: AsyncSession,
        stock_level_id: UUID,
    ) -> Optional[StockLevel]:

        stmt = (
            select(StockLevel)
            .where(
                StockLevel.stock_level_id == stock_level_id,
                StockLevel.deleted_at.is_(None),
            )
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()


stock_level_service = StockLevelService()
