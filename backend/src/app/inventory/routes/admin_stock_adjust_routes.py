# backend/src/app/inventory/routes/admin_stock_adjust_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_session

# ---------------------------------------------------------
# ✔️ Correct security imports (must be under src.app.auth...)
# ---------------------------------------------------------
from src.app.auth.services.org_context import get_current_org
from src.app.auth.services.dependencies import require_admin_org

from src.app.inventory.schemas.inv_schemas import (
    StockAdjustmentCreate,
    StockAdjustmentRead,
)

from src.app.inventory.services.stock_adjustments import stock_adjustment_service

router = APIRouter(
    prefix="/admin/stock-adjustments",
    tags=["admin_stock_adjustments"],
)


@router.post("/", response_model=StockAdjustmentRead, status_code=status.HTTP_201_CREATED)
async def adjust_stock(
    payload: StockAdjustmentCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    """
    Perform a stock adjustment.
    Only admins / managers / owners can do this.
    """

    # ✔️ Correct org extraction
    org_id = getattr(org_ctx, "org_id", None)

    data = payload.dict()
    data["org_id"] = org_id

    try:
        adjustment = await stock_adjustment_service.adjust(session, data)
        await session.commit()
        await session.refresh(adjustment)
        return adjustment

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
