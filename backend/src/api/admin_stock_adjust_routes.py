# backend/src/api/admin_stock_adjust_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.org_context import get_current_org
from src.core.security.dependencies import require_admin_org
from src.schemas.inv_schemas import StockAdjustmentCreate, StockAdjustmentRead
from src.services.inv.stock_adjustments import stock_adjustment_service


router = APIRouter(
    prefix="/admin/stock-adjustments",
    tags=["admin_stock_adjustments"],
)


# ---------------------------------------------------------
# CREATE STOCK ADJUSTMENT (admin/manager/owner only)
# ---------------------------------------------------------
@router.post("/", response_model=StockAdjustmentRead, status_code=status.HTTP_201_CREATED)
async def adjust_stock(
    payload: StockAdjustmentCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_admin_org),
):
    """
    Perform an inventory stock adjustment.
    Only admins/managers/owners can do this.
    """

    org_id = org_ctx["org"].org_id

    # Ensure adjustment is for the current org (safety)
    data = payload.dict()
    data["org_id"] = org_id

    try:
        adjustment = await stock_adjustment_service.adjust(session, data)
        await session.commit()
        await session.refresh(adjustment)
        return adjustment

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
