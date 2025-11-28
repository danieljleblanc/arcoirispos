# backend/src/app/inventory/routes/stock_levels_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_session

# ---------------------------------------------------------
# ✔️ Correct security imports (must come from src.app.auth...)
# ---------------------------------------------------------
from src.app.auth.services.org_context import get_current_org
from src.app.auth.services.dependencies import (
    require_any_staff_org,
    require_admin_org,
)

from src.app.inventory.schemas.inv_schemas import (
    StockLevelCreate,
    StockLevelRead,
    StockLevelUpdate,
)

from src.app.inventory.services.stock_level_service import stock_level_service

router = APIRouter(prefix="/stock-levels", tags=["stock-levels"])


# ---------------------------------------------------------
# LIST STOCK LEVELS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[StockLevelRead])
async def list_stock_levels(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    return await stock_level_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE STOCK LEVEL (any staff)
# ---------------------------------------------------------
@router.get("/{stock_level_id}", response_model=StockLevelRead)
async def get_stock_level(
    stock_level_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    stock_level = await stock_level_service.get_by_id(session, stock_level_id)

    if not stock_level or stock_level.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock level not found",
        )

    return stock_level


# ---------------------------------------------------------
# CREATE STOCK LEVEL (admin / manager / owner)
# ---------------------------------------------------------
@router.post("/", response_model=StockLevelRead, status_code=status.HTTP_201_CREATED)
async def create_stock_level(
    payload: StockLevelCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    data = payload.dict()
    data["org_id"] = org_id

    stock_level = await stock_level_service.create(session, data)
    await session.commit()
    await session.refresh(stock_level)
    return stock_level


# ---------------------------------------------------------
# UPDATE STOCK LEVEL (admin / manager / owner)
# ---------------------------------------------------------
@router.patch("/{stock_level_id}", response_model=StockLevelRead)
async def update_stock_level(
    stock_level_id: UUID,
    payload: StockLevelUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    stock_level = await stock_level_service.get_by_id(session, stock_level_id)

    if not stock_level or stock_level.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock level not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(stock_level, field, value)

    await session.commit()
    await session.refresh(stock_level)
    return stock_level
