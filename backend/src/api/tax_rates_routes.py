from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.pos_schemas import (
    TaxRateCreate,
    TaxRateRead,
    TaxRateUpdate,
)
from src.services.pos.tax_rates import tax_rate_service

router = APIRouter(prefix="/tax-rates", tags=["tax-rates"])


# ---- LIST ----
@router.get("/", response_model=List[TaxRateRead])
async def list_tax_rates(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await tax_rate_service.get_by_org(session, org_id, limit, offset)


# ---- GET BY ID ----
@router.get("/{tax_id}", response_model=TaxRateRead)
async def get_tax_rate(
    tax_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    tax_rate = await tax_rate_service.get_by_id(session, tax_id)
    if not tax_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found",
        )
    return tax_rate


# ---- CREATE ----
@router.post("/", response_model=TaxRateRead, status_code=status.HTTP_201_CREATED)
async def create_tax_rate(
    payload: TaxRateCreate,
    session: AsyncSession = Depends(get_session),
):
    tax_rate = await tax_rate_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(tax_rate)
    return tax_rate


# ---- UPDATE ----
@router.patch("/{tax_id}", response_model=TaxRateRead)
async def update_tax_rate(
    tax_id: UUID,
    payload: TaxRateUpdate,
    session: AsyncSession = Depends(get_session),
):
    tax_rate = await tax_rate_service.get_by_id(session, tax_id)
    if not tax_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(tax_rate, field, value)

    await session.commit()
    await session.refresh(tax_rate)
    return tax_rate


# ---- DELETE (SOFT DELETE FEATURE READY) ----
@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_rate(
    tax_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await tax_rate_service.delete(session, tax_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found",
        )
    await session.commit()
