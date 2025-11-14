from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session

from src.schemas.inventory_transaction_schemas import InventoryTransactionOut
from src.services.inventory_transaction_service import (
    list_transactions_for_item,
    list_transactions_for_location,
)

router = APIRouter(prefix="/inventory-transactions", tags=["Inventory Transactions"])


@router.get("/item/{item_id}", response_model=list[InventoryTransactionOut])
async def list_transactions_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await list_transactions_for_item(session, item_id)


@router.get("/location/{location_id}", response_model=list[InventoryTransactionOut])
async def list_transactions_location(
    location_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await list_transactions_for_location(session, location_id)
