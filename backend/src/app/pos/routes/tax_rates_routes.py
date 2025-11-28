# backend/src/app/pos/routes/tax_rates_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_session

# ---------------------------------------------------------
# Correct security imports
# ---------------------------------------------------------
from src.app.auth.services.org_context import get_current_org
from src.app.auth.services.dependencies import (
    require_any_staff_org,
    require_admin_org,
)

# ---------------------------------------------------------
# Schemas + Services
# ---------------------------------------------------------
from src.app.pos.schemas.pos_schemas import (
    TaxRateCreate,
    TaxRateRead,
    TaxRateUpdate,
)
from src.app.pos.services.tax_rate_service import tax_rate_service


router = APIRouter(prefix="/tax-rates", tags=["tax-rates"])


# ---------------------------------------------------------
# LIST TAX RATES (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[TaxRateRead])
async def list_tax_rates(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    return await tax_rate_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE TAX RATE (any staff)
# ---------------------------------------------------------
@router.get("/{tax_id}", response_model=TaxRateRead)
async def get_tax_rate(
    tax_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    tax_rate = await tax_rate_service.get_by_id(session, tax_id)

    if not tax_rate or tax_rate.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found",
        )

    return tax_rate


# ---------------------------------------------------------
# CREATE TAX RATE (admin / manager / owner)
# ---------------------------------------------------------
@router.post("/", response_model=TaxRateRead, status_code=status.HTTP_201_CREATED)
async def create_tax_rate(
    payload: TaxRateCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    data = payload.dict()
    data["org_id"] = org_id

    tax_rate = await tax_rate_service.create(session, data)
    await session.commit()
    await session.refresh(tax_rate)
    return tax_rate


# ---------------------------------------------------------
# UPDATE TAX RATE (admin / manager / owner)
# ---------------------------------------------------------
@router.patch("/{tax_id}", response_model=TaxRateRead)
async def update_tax_rate(
    tax_id: UUID,
    payload: TaxRateUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    tax_rate = await tax_rate_service.get_by_id(session, tax_id)

    if not tax_rate or tax_rate.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(tax_rate, field, value)

    await session.commit()
    await session.refresh(tax_rate)
    return tax_rate


# ---------------------------------------------------------
# DELETE TAX RATE (admin / manager / owner)
# ---------------------------------------------------------
@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_rate(
    tax_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    tax_rate = await tax_rate_service.get_by_id(session, tax_id)

    if not tax_rate or tax_rate.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found",
        )

    deleted = await tax_rate_service.delete_tax_rate(session, tax_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete tax rate",
        )

    await session.commit()
    return None
