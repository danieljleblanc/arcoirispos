# backend/src/app/pos/routes/sales_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_session

# ---------------------------------------------------------
# Security & Org Context
# ---------------------------------------------------------
from src.app.auth.services.org_context import get_current_org
from src.app.auth.services.dependencies import (
    require_any_staff_org,
    require_admin_org,
)

# ---------------------------------------------------------
# Schemas & Services
# ---------------------------------------------------------
from src.app.pos.schemas.pos_schemas import (
    SaleCreate,
    SaleRead,
    SaleReadWithLinesAndPayments,
    SaleUpdate,
)

from src.app.pos.services.sales_service import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


# ---------------------------------------------------------
# LIST SALES
# ---------------------------------------------------------
@router.get("/", response_model=List[SaleRead])
async def list_sales(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    """
    Returns a paginated list of sales for the current organization.
    Archived sales are automatically filtered by the service layer.
    """
    org_id = getattr(org_ctx, "org_id", None)
    return await sales_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SALE WITH RELATIONS
# ---------------------------------------------------------
@router.get("/{sale_id}", response_model=SaleReadWithLinesAndPayments)
async def get_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    sale = await sales_service.get_with_relations(session, sale_id)

    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    return sale


# ---------------------------------------------------------
# CREATE SALE
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=SaleReadWithLinesAndPayments,
    status_code=status.HTTP_201_CREATED,
)
async def create_sale(
    payload: SaleCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    """
    Creates a new sale using the checkout engine.
    Cashiers are allowed (any staff in the org).
    """
    org_id = getattr(org_ctx, "org_id", None)
    return await sales_service.create_sale(session, payload, org_id=org_id)


# ---------------------------------------------------------
# UPDATE SALE (PATCH + RECALCULATION)
# ---------------------------------------------------------
@router.patch(
    "/{sale_id}",
    response_model=SaleReadWithLinesAndPayments,
)
async def update_sale(
    sale_id: UUID,
    payload: SaleUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    sale = await sales_service.update_sale(session, sale_id, payload, org_id=org_id)

    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found or archived",
        )

    return sale


# ---------------------------------------------------------
# ARCHIVE SALE
# ---------------------------------------------------------
@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    sale = await sales_service.archive_sale(session, sale_id, org_id=org_id)

    if not sale or sale.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    return None
