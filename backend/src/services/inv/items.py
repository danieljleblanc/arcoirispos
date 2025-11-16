# backend/src/services/inv/items.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Item
from src.services.base_repository import BaseRepository


class ItemService(BaseRepository[Item]):
    def __init__(self) -> None:
        super().__init__(Item)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user = Depends(require_user)
    ) -> List[Item]:
        stmt = (
            select(Item)
            .where(
                Item.org_id == org_id,
                Item.deleted_at.is_(None),   # soft delete filter
            )
            .order_by(Item.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        item_id: UUID,
        user = Depends(require_user)
    ) -> Optional[Item]:
        stmt = select(Item).where(
            Item.item_id == item_id,
            Item.deleted_at.is_(None),       # soft delete filter
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_item(
        self,
        session: AsyncSession,
        item_id: UUID,
        user = Depends(require_roles(["owner", "admin", "inventory"]))
    ) -> Optional[Item]:
        """
        Soft-delete the item using BaseRepository logic.
        """
        return await self.delete(session, item_id)


item_service = ItemService()
