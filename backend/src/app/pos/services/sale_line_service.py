from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.pos.models.sale_models import SaleLine
from src.app.core.base_repository import BaseRepository


class SaleLineService(BaseRepository[SaleLine]):
    def __init__(self) -> None:
        super().__init__(SaleLine)

    async def get_by_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
    ) -> List[SaleLine]:
        stmt = (
            select(SaleLine)
            .where(SaleLine.sale_id == sale_id)
            .order_by(SaleLine.line_number.asc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        sale_line_id: UUID,
    ) -> Optional[SaleLine]:
        stmt = select(SaleLine).where(SaleLine.sale_line_id == sale_line_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SaleLine]:
        stmt = (
            select(SaleLine)
            .where(SaleLine.org_id == org_id)
            .order_by(SaleLine.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()


sale_line_service = SaleLineService()
