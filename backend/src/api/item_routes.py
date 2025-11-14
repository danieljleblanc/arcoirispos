from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.core.database import get_session
from src.models.item import Item
from src.schemas.item_schemas import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["Items"])


# ─────────────────────────────────────────────
# CREATE ITEM
# ─────────────────────────────────────────────
@router.post("/", response_model=ItemOut)
async def create_item(
    payload: ItemCreate,
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    new_item = Item(
        name=payload.name,
        description=payload.description,
        sku=payload.sku,
        price=payload.price,
        organization_id=organization_id
    )
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


# ─────────────────────────────────────────────
# GET SINGLE ITEM
# ─────────────────────────────────────────────
@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# ─────────────────────────────────────────────
# LIST ITEMS
# ─────────────────────────────────────────────
@router.get("/", response_model=list[ItemOut])
async def list_items(
    organization_id: int = 1,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Item)
        .where(Item.organization_id == organization_id)
        .order_by(Item.name.asc())
        .limit(limit)
    )
    return result.scalars().all()


# ─────────────────────────────────────────────
# UPDATE ITEM
# ─────────────────────────────────────────────
@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: int,
    payload: ItemCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        update(Item)
        .where(Item.id == item_id)
        .values(
            name=payload.name,
            description=payload.description,
            sku=payload.sku,
            price=payload.price
        )
        .returning(Item)
    )

    item = result.fetchone()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.commit()
    return item[0]


# ─────────────────────────────────────────────
# DELETE ITEM
# ─────────────────────────────────────────────
@router.delete("/{item_id}", response_model=dict)
async def delete_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        delete(Item).where(Item.id == item_id).returning(Item.id)
    )
    deleted = result.scalar()

    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.commit()
    return {"status": "deleted", "item_id": item_id}
