# backend/src/services/pos/sales.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Sale, SaleLine, Payment
from src.services.base_repository import BaseRepository
from src.schemas.pos_schemas import SaleCreate


class SalesService(BaseRepository[Sale]):
    def __init__(self) -> None:
        super().__init__(Sale)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Sale]:
        stmt = (
            select(Sale)
            .where(Sale.org_id == org_id)
            .order_by(Sale.sale_date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    async def get_with_relations(
        self,
        session: AsyncSession,
        sale_id: UUID,
    ) -> Optional[Sale]:
        stmt = select(Sale).where(Sale.sale_id == sale_id)
        result = await session.execute(stmt)
        sale = result.scalar_one_or_none()
        if sale:
            _ = sale.sale_lines
            _ = sale.payments
        return sale

    async def create_sale(
        self,
        session: AsyncSession,
        payload: SaleCreate,
    ) -> Sale:
        data = payload.dict()
        lines_data = data.pop("lines")
        payments_data = data.pop("payments", [])

        sale = Sale(**data)

        for line in lines_data:
            sale_line = SaleLine(**line)
            sale.sale_lines.append(sale_line)

        for payment in payments_data:
            payment_obj = Payment(**payment)
            sale.payments.append(payment_obj)

        session.add(sale)
        await session.commit()
        await session.refresh(sale)
        _ = sale.sale_lines
        _ = sale.payments
        return sale


sales_service = SalesService()
