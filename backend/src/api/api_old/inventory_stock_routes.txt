from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.stock_level_schemas import StockLevelOut
from src.services.stock_service import (
    get_stock_level, set_stock, adjust_stock, list_stock_for_item
)

router = APIRouter(prefix="/stock", tags=["Stock Levels"])


@router.get("/{item_id}/{location_id}", response_model=StockLevelOut)
async def get_stock(item_id: int, location_id: int,
                    session: AsyncSession = Depends(get_session)):
    stock = await get_stock_level(session, item_id, location_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.post("/{item_id}/{location_id}/set", response_model=StockLevelOut)
async def set_stock_level(
    item_id: int,
    location_id: int,
    quantity: int,
    session: AsyncSession = Depends(get_session),
):
    return await set_stock(session, item_id, location_id, quantity)


@router.post("/{item_id}/{location_id}/adjust")
async def adjust_stock_endpoint(
    item_id: int,
    location_id: int,
    quantity_change: int,
    transaction_type: str,
    reference_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    stock, tx = await adjust_stock(
        session, item_id, location_id,
        quantity_change, transaction_type, reference_id
    )
    return {"stock": stock, "transaction": tx}


@router.get("/item/{item_id}", response_model=list[StockLevelOut])
async def list_stock_for_item_endpoint(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await list_stock_for_item(session, item_id)
