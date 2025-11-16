#backend/src/services/inv/stock_adjustments.py

from decimal import Decimal
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StockMovement, StockLevel
from src.schemas.inv_schemas import StockAdjustmentCreate


class StockAdjustmentService:
    async def adjust(
        self,
        session: AsyncSession,
        payload: StockAdjustmentCreate,
    ):
        # 1: Update stock_level.quantity_on_hand
        stmt = (
            await session.execute(
                StockLevel.__table__
                .select()
                .where(StockLevel.org_id == payload.org_id)
                .where(StockLevel.item_id == payload.item_id)
                .where(StockLevel.location_id == payload.location_id)
            )
        )

        stock_level = stmt.scalar_one_or_none()

        if not stock_level:
            raise ValueError("Stock level not found for org/item/location")

        # Apply adjustment
        stock_level.quantity_on_hand += payload.quantity_delta

        # 2: Log stock movement with reason
        movement = StockMovement(
            org_id=payload.org_id,
            item_id=payload.item_id,
            location_id=payload.location_id,
            source_type="admin_adjustment",
            source_id=None,
            quantity_delta=payload.quantity_delta,
            unit_cost=None,
            occurred_at=datetime.utcnow(),
        )

        movement.notes = payload.reason

        session.add(movement)
        await session.commit()
        await session.refresh(movement)

        return movement


stock_adjustment_service = StockAdjustmentService()
