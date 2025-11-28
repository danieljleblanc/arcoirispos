# backend/src/app/core/base_repository.py

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.base import Base  # ✅ FIXED import


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Shared CRUD behavior.
    Automatically handles:
      - Primary key discovery
      - Soft delete (if model has deleted_at column)
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._has_deleted_at = hasattr(model, "deleted_at")

    def _pk(self):
        """Dynamically return the model's primary key column."""
        return list(self.model.__table__.primary_key.columns)[0]

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------
    async def get(self, session: AsyncSession, pk: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self._pk() == pk)

        if self._has_deleted_at:
            stmt = stmt.where(self.model.deleted_at.is_(None))

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------
    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[ModelType]:

        stmt = select(self.model).limit(limit).offset(offset)

        if self._has_deleted_at and not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))

        result = await session.execute(stmt)
        return result.scalars().all()

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------
    async def create(
        self,
        session: AsyncSession,
        obj_in: Dict[str, Any],
    ) -> ModelType:
        obj = self.model(**obj_in)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)  # ensure outbound object is fresh
        return obj

    # ---------------------------------------------------------
    # DELETE (soft or hard)
    # ---------------------------------------------------------
    async def delete(self, session: AsyncSession, pk: Any) -> Optional[ModelType]:
        obj = await self.get(session, pk)
        if not obj:
            return None

        if self._has_deleted_at:
            obj.deleted_at = datetime.now(timezone.utc)
            await session.flush()
            await session.refresh(obj)
            return obj

        # Hard delete fallback
        await session.delete(obj)
        return obj