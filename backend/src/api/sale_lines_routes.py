# backend/src/api/sale_lines_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import require_any_staff, require_admin
from src.schemas.pos_schemas import (
    SaleLineCreate,
    SaleLineRead,
    SaleLineUpdate,
)
from src.services.pos.sale_lines import sale_line_service

router = APIRouter(prefix="/sale_lines", tags=["sale_lines"])


# ---------------------------------------------------------
# LIST BY ORG (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[SaleLineRead])
async def list_sale_lines(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    return await sale_line_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# LIST BY SALE (any staff)
# ---------------------------------------------------------
@router.get("/sale/{sale_id}", response_model=List[SaleLineRead])
async def list_sale_lines_for_sale(
    sale_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    # RBAC via org_id; service filters by sale_id.
    return await sale_line_service.get_by_sale(session, sale_id)


# ---------------------------------------------------------
# GET SINGLE SALE LINE (any staff)
# ---------------------------------------------------------
@router.get("/{sale_line_id}", response_model=SaleLineRead)
async def get_sale_line(
    sale_line_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    sl = await sale_line_service.get_by_id(session, sale_line_id)
    if not sl or sl.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale line not found",
        )
    return sl


# ---------------------------------------------------------
# CREATE SALE LINE (admin / manager / owner)
# ---------------------------------------------------------
@router.post("/", response_model=SaleLineRead, status_code=status.HTTP_201_CREATED)
async def create_sale_line(
    org_id: UUID,
    payload: SaleLineCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    data = payload.dict()
    data["org_id"] = org_id

    sl = await sale_line_service.create(session, data)
    await session.commit()
    await session.refresh(sl)
    return sl


# ---------------------------------------------------------
# UPDATE SALE LINE (admin / manager / owner)
# ---------------------------------------------------------
@router.patch("/{sale_line_id}", response_model=SaleLineRead)
async def update_sale_line(
    sale_line_id: UUID,
    org_id: UUID,
    payload: SaleLineUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    sl = await sale_line_service.get_by_id(session, sale_line_id)
    if not sl or sl.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale line not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(sl, field, value)

    await session.commit()
    await session.refresh(sl)
    return sl


# ---------------------------------------------------------
# DELETE SALE LINE (admin / manager / owner)
# ---------------------------------------------------------
@router.delete("/{sale_line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale_line(
    sale_line_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    sl = await sale_line_service.get_by_id(session, sale_line_id)
    if not sl or sl.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale line not found",
        )

    deleted = await sale_line_service.delete_sale_line(session, sale_line_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale line not found",
        )

    await session.commit()
    return None
