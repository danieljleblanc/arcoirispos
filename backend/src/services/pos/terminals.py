from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Terminal
from src.services.base_repository import BaseRepository


class TerminalService(BaseRepository[Terminal]):
    def __init__(self) -> None:
        super().__init__(Terminal)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user = Depends(require_user)
    ) -> List[Terminal]:
        stmt = (
            select(Terminal)
            .where(Terminal.org_id == org_id)
            .order_by(Terminal.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        terminal_id: UUID,
        user = Depends(require_user)
    ) -> Optional[Terminal]:
        stmt = select(Terminal).where(Terminal.terminal_id == terminal_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


terminal_service = TerminalService()
