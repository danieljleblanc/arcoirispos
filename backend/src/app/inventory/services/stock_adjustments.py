# backend/src/app/inventory/services/stock_adjustments.py

from decimal import Decimal
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.inventory.models.stock_movement_models import StockMovement
from src.app.inventory.models.stock_level_models import StockLevel
from src.app.inventory.schemas.inv_schemas import StockAdjustmentCreate


class StockAdjustmentService:
    async def adjust(
        self,
        session: AsyncSession,
        payload: StockAdjustmentCreate,
    ):
        # ---------------------------------------------------------
        # 1. Fetch StockLevel ORM row
        # ---------------------------------------------------------
        stmt = (
            select(StockLevel)
            .where(StockLevel.org_id == payload.org_id)
            .where(StockLevel.item_id == payload.item_id)
            .where(StockLevel.location_id == payload.location_id)
            .where(StockLevel.deleted_at.is_(None))
        )

        result = await session.execute(stmt)
        stock_level = result.scalar_one_or_none()

        if not stock_level:
            raise ValueError("Stock level not found for org/item/location")

        # ---------------------------------------------------------
        # 2. Apply quantity adjustment
        # ---------------------------------------------------------
        stock_level.quantity_on_hand += payload.quantity_delta

        # ---------------------------------------------------------
        # 3. Log stock movement record
        # ---------------------------------------------------------
        movement = StockMovement(
            org_id=payload.org_id,
            item_id=payload.item_id,
            location_id=payload.location_id,
            source_type="admin_adjustment",
            source_id=None,
            quantity_delta=payload.quantity_delta,
            unit_cost=None,
            occurred_at=datetime.utcnow(),
            notes=payload.reason,
        )

        session.add(movement)

        # ---------------------------------------------------------
        # 4. Finalize transaction
        # ---------------------------------------------------------
        await session.commit()
        await session.refresh(movement)

        return movement


stock_adjustment_service = StockAdjustmentService()
