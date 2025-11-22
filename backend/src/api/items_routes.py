# backend/src/api/items_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.inv_schemas import ItemCreate, ItemRead, ItemUpdate
from src.services.inv.items import item_service
from src.core.security.dependencies import require_any_staff, require_admin

router = APIRouter(prefix="/items", tags=["items"])


# ---------------------------------------------------------
# LIST ITEMS (any authenticated staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[ItemRead])
async def list_items(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    return await item_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE ITEM (any authenticated staff)
# ---------------------------------------------------------
@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
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
    org_id: UUID,
    payload: ItemCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
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
    org_id: UUID,
    payload: ItemUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
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
# DELETE (SOFT-DELETE) ITEM (admin/manager/owner)
# ---------------------------------------------------------
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
    item = await item_service.get_by_id(session, item_id)
    if not item or item.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    deleted = await item_service.delete_item(session, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or could not be deleted",
        )

    await session.commit()
    return None
