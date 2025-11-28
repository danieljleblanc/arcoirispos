from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.inventory_transaction import InventoryTransaction


# ─────────────────────────────────────────────
# LIST ALL TRANSACTIONS FOR AN ITEM
# ─────────────────────────────────────────────
async def list_transactions_for_item(session: AsyncSession, item_id: int):
    result = await session.execute(
        select(InventoryTransaction)
        .where(InventoryTransaction.item_id == item_id)
        .order_by(InventoryTransaction.created_at.desc())
    )
    return result.scalars().all()


# ─────────────────────────────────────────────
# LIST ALL TRANSACTIONS FOR LOCATION
# ─────────────────────────────────────────────
async def list_transactions_for_location(session: AsyncSession, location_id: int):
    result = await session.execute(
        select(InventoryTransaction)
        .where(InventoryTransaction.location_id == location_id)
        .order_by(InventoryTransaction.created_at.desc())
    )
    return result.scalars().all()
