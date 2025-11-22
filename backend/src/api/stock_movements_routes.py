# backend/src/api/stock_movements_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import require_any_staff, require_admin
from src.schemas.inv_schemas import (
    StockMovementCreate,
    StockMovementRead,
)
from src.services.inv.stock_movements import stock_movement_service


router = APIRouter(prefix="/stock-movements", tags=["stock-movements"])


# ---------------------------------------------------------
# LIST MOVEMENTS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[StockMovementRead])
async def list_stock_movements(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    return await stock_movement_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE MOVEMENT (any staff)
# ---------------------------------------------------------
@router.get("/{movement_id}", response_model=StockMovementRead)
async def get_stock_movement(
    movement_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    movement = await stock_movement_service.get_by_id(session, movement_id)

    if not movement or movement.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock movement not found",
        )

    return movement


# ---------------------------------------------------------
# CREATE MOVEMENT (admin/manager/owner ONLY)
# ---------------------------------------------------------
@router.post("/", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED)
async def create_stock_movement(
    org_id: UUID,
    payload: StockMovementCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    data = payload.dict()
    data["org_id"] = org_id

    movement = await stock_movement_service.create(session, data)
    await session.commit()
    await session.refresh(movement)
    return movement
