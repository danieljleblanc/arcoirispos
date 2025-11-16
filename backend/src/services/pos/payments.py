from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Payment
from src.services.base_repository import BaseRepository


class PaymentService(BaseRepository[Payment]):
    def __init__(self) -> None:
        super().__init__(Payment)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user = Depends(require_user)
    ) -> List[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.org_id == org_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
        user = Depends(require_user)
    ) -> List[Payment]:
        stmt = select(Payment).where(Payment.sale_id == sale_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        payment_id: UUID,
        user = Depends(require_user)
    ) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.payment_id == payment_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


payment_service = PaymentService()
