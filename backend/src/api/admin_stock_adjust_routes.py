#backend/src/api/admin_stock_adjust_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.inv_schemas import StockAdjustmentCreate, StockAdjustmentRead
from src.services.inv.stock_adjustments import stock_adjustment_service

router = APIRouter(
    prefix="/admin/stock-adjustments",
    tags=["admin_stock_adjustments"]
)

@router.post("/", response_model=StockAdjustmentRead)
async def adjust_stock(
    payload: StockAdjustmentCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        movement = await stock_adjustment_service.adjust(session, payload)
        return movement
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
