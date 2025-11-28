from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models.stock_level import StockLevel
from src.models.inventory_transaction import InventoryTransaction


# ─────────────────────────────────────────────
# GET STOCK LEVEL
# ─────────────────────────────────────────────
async def get_stock_level(session: AsyncSession, item_id: int, location_id: int):
    result = await session.execute(
        select(StockLevel)
        .where(StockLevel.item_id == item_id)
        .where(StockLevel.location_id == location_id)
    )
    return result.scalar_one_or_none()


# ─────────────────────────────────────────────
# SET STOCK LEVEL (Used for initialization or corrections)
# ─────────────────────────────────────────────
async def set_stock(session: AsyncSession, item_id: int, location_id: int, quantity: int):
    stock = await get_stock_level(session, item_id, location_id)

    if stock:
        stock.quantity = quantity
    else:
        stock = StockLevel(
            item_id=item_id,
            location_id=location_id,
            quantity=quantity
        )
        session.add(stock)

    await session.commit()
    return stock


# ─────────────────────────────────────────────
# ADJUST STOCK LEVEL (+ or -)
# ─────────────────────────────────────────────
async def adjust_stock(session: AsyncSession, item_id: int, location_id: int,
                       quantity_change: int, transaction_type: str,
                       reference_id: int | None = None):

    # 1. Update stock levels
    stock = await get_stock_level(session, item_id, location_id)

    if not stock:
        stock = StockLevel(item_id=item_id, location_id=location_id, quantity=0)
        session.add(stock)

    stock.quantity += quantity_change

    # 2. Write inventory transaction log
    tx = InventoryTransaction(
        item_id=item_id,
        location_id=location_id,
        quantity_change=quantity_change,
        transaction_type=transaction_type,
        reference_id=reference_id
    )
    session.add(tx)

    await session.commit()
    return stock, tx


# ─────────────────────────────────────────────
# GET STOCK SUMMARY FOR ITEM
# ─────────────────────────────────────────────
async def list_stock_for_item(session: AsyncSession, item_id: int):
    result = await session.execute(
        select(StockLevel).where(StockLevel.item_id == item_id)
    )
    return result.scalars().all()
