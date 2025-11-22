# backend/src/api/sales_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import (
    require_any_staff,
    require_admin,
)
from src.schemas.pos_schemas import (
    SaleCreate,
    SaleRead,
    SaleReadWithLinesAndPayments,
    SaleUpdate,
)
from src.services.pos.sales import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


# ---------------------------------------------------------
# LIST SALES (READ-ONLY, ANY STAFF IN ORG)
# ---------------------------------------------------------
@router.get("/", response_model=List[SaleRead])
async def list_sales(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    """
    Returns a paginated list of sales for an org.
    Archived sales are excluded at service layer.
    """
    return await sales_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET A SINGLE SALE WITH LINES & PAYMENTS
# ---------------------------------------------------------
@router.get("/{sale_id}", response_model=SaleReadWithLinesAndPayments)
async def get_sale(
    sale_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    sale = await sales_service.get_with_relations(session, sale_id)
    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )
    return sale


# ---------------------------------------------------------
# CREATE SALE (CHECKOUT) — allow ANY STAFF (cashiers!)
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=SaleReadWithLinesAndPayments,
    status_code=status.HTTP_201_CREATED,
)
async def create_sale(
    org_id: UUID,
    payload: SaleCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    """
    Creates a sale using the checkout engine.

    NOTE: For safety, we can optionally enforce that the incoming payload's
    org_id (if present) matches the org_id query param.
    """
    # Defensive check if SaleCreate includes org_id
    if hasattr(payload, "org_id") and payload.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload org_id does not match request org_id",
        )

    sale = await sales_service.create_sale(session, payload)
    return sale


# ---------------------------------------------------------
# UPDATE SALE (PATCH + RECALC) — admin/manager/owner only
# ---------------------------------------------------------
@router.patch(
    "/{sale_id}",
    response_model=SaleReadWithLinesAndPayments,
)
async def update_sale(
    sale_id: UUID,
    org_id: UUID,
    payload: SaleUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    """
    Updates a sale by merging the PATCH payload,
    recalculating totals, and replacing lines/payments.
    """
    sale = await sales_service.update_sale(session, sale_id, payload)
    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found or archived",
        )
    return sale


# ---------------------------------------------------------
# ARCHIVE SALE (SOFT DELETE)
# ---------------------------------------------------------
@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def archive_sale(
    sale_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    sale = await sales_service.archive_sale(session, sale_id)
    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    return None
