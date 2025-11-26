# backend/src/services/pos/payments.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.pos.models.payment_models import Payment
from src.app.core.base_repository import BaseRepository


class PaymentService(BaseRepository[Payment]):
    def __init__(self) -> None:
        super().__init__(Payment)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
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
    ) -> List[Payment]:
        stmt = select(Payment).where(Payment.sale_id == sale_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        payment_id: UUID,
    ) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.payment_id == payment_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


payment_service = PaymentService()
