from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StockMovement
from src.services.base_repository import BaseRepository


class StockMovementService(BaseRepository[StockMovement]):
    def __init__(self) -> None:
        super().__init__(StockMovement)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StockMovement]:
        stmt = (
            select(StockMovement)
            .where(StockMovement.org_id == org_id)
            .order_by(StockMovement.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        movement_id: UUID,
    ) -> Optional[StockMovement]:
        stmt = select(StockMovement).where(
            StockMovement.movement_id == movement_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


stock_movement_service = StockMovementService()
