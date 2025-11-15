from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.inv_schemas import (
    StockMovementCreate,
    StockMovementRead,
)
from src.services.inv.stock_movements import stock_movement_service


router = APIRouter(prefix="/stock-movements", tags=["inventory: stock movements"])


@router.get("/", response_model=List[StockMovementRead])
async def list_stock_movements(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await stock_movement_service.get_by_org(session, org_id, limit, offset)


@router.get("/{movement_id}", response_model=StockMovementRead)
async def get_stock_movement(
    movement_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    movement = await stock_movement_service.get_by_id(session, movement_id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock movement not found",
        )
    return movement


@router.post("/", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED)
async def create_stock_movement(
    payload: StockMovementCreate,
    session: AsyncSession = Depends(get_session),
):
    movement = await stock_movement_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(movement)
    return movement
