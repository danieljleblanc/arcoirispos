# backend/src/api/items_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.inv_schemas import ItemCreate, ItemRead, ItemUpdate
from src.services.inv.items import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemRead])
async def list_items(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await item_service.get_by_org(session, org_id, limit, offset)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    item = await item_service.get_by_id(session, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_roles(["admin", "owner"]))
):
    item = await item_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: UUID,
    payload: ItemUpdate,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_roles(["admin", "owner"]))
):
    item = await item_service.get_by_id(session, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await item_service.delete_item(session, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    await session.commit()
    return None
        

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)

    await session.commit()
    await session.refresh(item)
    return item
