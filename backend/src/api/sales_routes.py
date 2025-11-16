# backend/src/api/sales_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import require_user, require_roles
from src.schemas.pos_schemas import SaleCreate, SaleRead, SaleUpdate
from src.services.pos.sales_service import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


# ---------------------------------------------------------
# LIST SALES (authenticated user only)
# ---------------------------------------------------------
@router.get("/", response_model=List[SaleRead])
async def list_sales(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_user),
):
    return await sales_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE SALE
# ---------------------------------------------------------
@router.get("/{sale_id}", response_model=SaleRead)
async def get_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_user),
):
    sale = await sales_service.get_with_relations(session, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )
    return sale


# ---------------------------------------------------------
# CREATE SALE (cashier/admin/owner)
# ---------------------------------------------------------
@router.post("/", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
async def create_sale(
    payload: SaleCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_roles(["cashier", "admin", "owner"])),
):
    sale = await sales_service.create_sale(session, payload)
    return sale


# ---------------------------------------------------------
# UPDATE SALE (admin/owner)
# ---------------------------------------------------------
@router.patch("/{sale_id}", response_model=SaleRead)
async def update_sale(
    sale_id: UUID,
    payload: SaleUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_roles(["admin", "owner"])),
):
    sale = await sales_service.get_with_relations(session, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    # Apply updates
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(sale, field, value)

    await session.commit()
    await session.refresh(sale)
    return sale


# ---------------------------------------------------------
# ARCHIVE (SOFT DELETE) SALE (admin/owner)
# ---------------------------------------------------------
@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_roles(["admin", "owner"])),
):
    archived = await sales_service.archive_sale(session, sale_id)
    if not archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )
    return None
