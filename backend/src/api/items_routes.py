# backend/src/api/items_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.org_context import get_current_org
from src.core.security.dependencies import require_any_staff_org, require_admin_org
from src.schemas.inv_schemas import (
    ItemCreate,
    ItemRead,
    ItemUpdate,
)
from src.services.inv.items import item_service

router = APIRouter(prefix="/items", tags=["items"])


# ---------------------------------------------------------
# LIST ITEMS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[ItemRead])
async def list_items(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    org_id = org_ctx["org"].org_id
    return await item_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE ITEM (any staff)
# ---------------------------------------------------------
@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_any_staff_org),
):
    org_id = org_ctx["org"].org_id
    item = await item_service.get_by_id(session, item_id)

    if not item or item.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item


# ---------------------------------------------------------
# CREATE ITEM (admin/manager/owner)
# ---------------------------------------------------------
@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = org_ctx["org"].org_id
    data = payload.dict()
    data["org_id"] = org_id

    item = await item_service.create(session, data)
    await session.commit()
    await session.refresh(item)
    return item


# ---------------------------------------------------------
# UPDATE ITEM (admin/manager/owner)
# ---------------------------------------------------------
@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: UUID,
    payload: ItemUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = org_ctx["org"].org_id
    item = await item_service.get_by_id(session, item_id)

    if not item or item.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    update_fields = payload.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(item, field, value)

    await session.commit()
    await session.refresh(item)
    return item


# ---------------------------------------------------------
# DELETE ITEM (admin/manager/owner)
# ---------------------------------------------------------
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx=Depends(get_current_org),
    user=Depends(require_admin_org),
):
    org_id = org_ctx["org"].org_id
    item = await item_service.get_by_id(session, item_id)

    if not item or item.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    deleted = await item_service.delete_item(session, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete item",
        )

    await session.commit()
    return None
