from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.pos.models.tax_rate_models import TaxRate
from src.app.core.base_repository import BaseRepository


class TaxRateService(BaseRepository[TaxRate]):
    def __init__(self) -> None:
        super().__init__(TaxRate)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TaxRate]:
        stmt = (
            select(TaxRate)
            .where(TaxRate.org_id == org_id)
            .order_by(TaxRate.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        tax_id: UUID,
    ) -> Optional[TaxRate]:
        stmt = select(TaxRate).where(TaxRate.tax_id == tax_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


tax_rate_service = TaxRateService()
