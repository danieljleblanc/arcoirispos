# backend/src/api/admin_stock_adjust_routes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import require_admin
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
    org_id: UUID,
    payload: StockAdjustmentCreate,
    session: AsyncSession = Depends(get_session),
    user_ctx=Depends(require_admin),
):
    """
    Perform an inventory stock adjustment.
    Only admins/managers/owners can do this.
    """
    try:
        # For now, we trust payload.org_id or internal service checks.
        # If needed later, we can enforce payload.org_id == org_id
        adjustment = await stock_adjustment_service.adjust(session, payload)
        await session.commit()
        await session.refresh(adjustment)
        return adjustment

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
