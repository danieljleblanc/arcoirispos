from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.org_context import get_current_org
from src.core.security.dependencies import (
    require_any_staff_org,
    require_admin_org,
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
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    """
    Returns a paginated list of sales for the active org.
    Archived sales are excluded at service layer.
    """
    org_id = org_ctx["org"].org_id
    return await sales_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET A SINGLE SALE WITH LINES & PAYMENTS (any staff)
# ---------------------------------------------------------
@router.get("/{sale_id}", response_model=SaleReadWithLinesAndPayments)
async def get_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = org_ctx["org"].org_id
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
    payload: SaleCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    """
    Creates a sale using the checkout engine, for the active org.
    """

    org_id = org_ctx["org"].org_id
    sale = await sales_service.create_sale(session, payload, org_id=org_id)
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
    payload: SaleUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    """
    Updates a sale by merging the PATCH payload,
    recalculating totals, and replacing lines/payments.
    """

    org_id = org_ctx["org"].org_id
    sale = await sales_service.update_sale(session, sale_id, payload, org_id=org_id)

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
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = org_ctx["org"].org_id
    sale = await sales_service.archive_sale(session, sale_id, org_id=org_id)
    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    return None
