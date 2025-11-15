# backend/src/api/stock_levels_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.inv_schemas import (
    StockLevelCreate,
    StockLevelRead,
    StockLevelUpdate,
)
from src.services.inv.stock_levels import stock_level_service

router = APIRouter(prefix="/stock-levels", tags=["stock_levels"])


@router.get("/", response_model=List[StockLevelRead])
async def list_stock_levels(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await stock_level_service.get_by_org(session, org_id, limit, offset)


@router.get("/{stock_level_id}", response_model=StockLevelRead)
async def get_stock_level(
    stock_level_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    stock_level = await stock_level_service.get_by_id(session, stock_level_id)
    if not stock_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock level not found",
        )
    return stock_level


@router.post("/", response_model=StockLevelRead, status_code=status.HTTP_201_CREATED)
async def create_stock_level(
    payload: StockLevelCreate,
    session: AsyncSession = Depends(get_session),
):
    stock_level = await stock_level_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(stock_level)
    return stock_level


@router.patch("/{stock_level_id}", response_model=StockLevelRead)
async def update_stock_level(
    stock_level_id: UUID,
    payload: StockLevelUpdate,
    session: AsyncSession = Depends(get_session),
):
    stock_level = await stock_level_service.get_by_id(session, stock_level_id)
    if not stock_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock level not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(stock_level, field, value)

    await session.commit()
    await session.refresh(stock_level)
    return stock_level
