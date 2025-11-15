# backend/src/services/pos/customers.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Customer
from src.services.base_repository import BaseRepository


class CustomerService(BaseRepository[Customer]):
    def __init__(self) -> None:
        super().__init__(Customer)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.org_id == org_id)
            .where(Customer.deleted_at.is_(None))  # hide soft-deleted rows
            .order_by(Customer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        customer_id: UUID,
    ) -> Optional[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .where(Customer.deleted_at.is_(None))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    # ⭐ NEW: Soft-delete support for Customers
    async def delete_customer(
        self,
        session: AsyncSession,
        customer_id: UUID,
    ) -> Optional[Customer]:
        return await super().delete(session, customer_id)


customer_service = CustomerService()
