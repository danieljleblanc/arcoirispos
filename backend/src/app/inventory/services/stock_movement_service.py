# backend/src/app/inventory/services/stock_movements.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.inventory.models.stock_movement_models import StockMovement
from src.app.core.base_repository import BaseRepository


class StockMovementService(BaseRepository[StockMovement]):
    def __init__(self) -> None:
        super().__init__(StockMovement)

    # ---------------------------------------------------------
    # LIST MOVEMENTS BY ORG
    # ---------------------------------------------------------
    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StockMovement]:

        stmt = (
            select(StockMovement)
            .where(
                StockMovement.org_id == org_id,
                StockMovement.deleted_at.is_(None),
            )
            .order_by(StockMovement.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    # ---------------------------------------------------------
    # GET SINGLE MOVEMENT
    # ---------------------------------------------------------
    async def get_by_id(
        self,
        session: AsyncSession,
        movement_id: UUID,
    ) -> Optional[StockMovement]:

        stmt = (
            select(StockMovement)
            .where(
                StockMovement.movement_id == movement_id,
                StockMovement.deleted_at.is_(None),
            )
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()


stock_movement_service = StockMovementService()
