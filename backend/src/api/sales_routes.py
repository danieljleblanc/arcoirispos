# backend/src/api/sales_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.pos_schemas import (
    SaleCreate,
    SaleReadWithLinesAndPayments,
)
from src.services.pos.sales import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=List[SaleReadWithLinesAndPayments])
async def list_sales(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    sales = await sales_service.get_by_org(session, org_id, limit, offset)
    return sales


@router.get("/{sale_id}", response_model=SaleReadWithLinesAndPayments)
async def get_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    sale = await sales_service.get_with_relations(session, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )
    return sale


@router.post("/", response_model=SaleReadWithLinesAndPayments, status_code=status.HTTP_201_CREATED)
async def create_sale(
    payload: SaleCreate,
    session: AsyncSession = Depends(get_session),
):
    sale = await sales_service.create_sale(session, payload)
    return sale
