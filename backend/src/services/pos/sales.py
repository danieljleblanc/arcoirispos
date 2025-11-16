from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Sale, SaleLine, Payment
from src.services.base_repository import BaseRepository
from src.schemas.pos_schemas import SaleCreate
from src.services.pos.checkout_service import checkout_service


class SalesService(BaseRepository[Sale]):
    def __init__(self) -> None:
        super().__init__(Sale)

    # ---------------------------------------------------------
    # LIST SALES (EXCLUDES ARCHIVED)
    # ---------------------------------------------------------
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
            .where(Sale.status != "archived")   # <–– Option A soft-delete filter
            .order_by(Sale.sale_date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    # ---------------------------------------------------------
    # GET SINGLE SALE + RELATIONS (EXCLUDES ARCHIVED)
    # ---------------------------------------------------------
    async def get_with_relations(
        self,
        session: AsyncSession,
        sale_id: UUID,
    ) -> Optional[Sale]:
        stmt = (
            select(Sale)
            .where(Sale.sale_id == sale_id)
            .where(Sale.status != "archived")   # <–– do not load archived
        )
        result = await session.execute(stmt)
        sale = result.scalar_one_or_none()

        if sale:
            # Access relationships so ORM loads them
            _ = sale.sale_lines
            _ = sale.payments

        return sale

    # ---------------------------------------------------------
    # CREATE SALE (CALCULATED VIA CHECKOUT ENGINE)
    # ---------------------------------------------------------
    async def create_sale(
        self,
        session: AsyncSession,
        payload: SaleCreate,
    ) -> Sale:

        # 1. Run checkout engine
        calc = await checkout_service.calculate(session, payload)

        # 2. Create main Sale record
        sale = Sale(
            org_id=payload.org_id,
            terminal_id=payload.terminal_id,
            customer_id=payload.customer_id,
            sale_number=payload.sale_number,
            status=payload.status,
            sale_type=payload.sale_type,
            subtotal=calc["subtotal"],
            tax_total=calc["tax_total"],
            discount_total=calc["discount_total"],
            grand_total=calc["grand_total"],
            amount_paid=calc["amount_paid"],
            balance_due=calc["balance_due"],
            sale_date=payload.sale_date,
            notes=payload.notes,
            created_by=payload.created_by,
        )

        session.add(sale)
        await session.flush()  # populate sale.sale_id

        # 3. Create SaleLines based on engine results
        for raw_line, engine_line in zip(payload.lines, calc["lines"]):
            line = SaleLine(
                sale_id=sale.sale_id,
                org_id=sale.org_id,
                item_id=raw_line.item_id,
                line_number=raw_line.line_number,
                description=raw_line.description,
                quantity=engine_line["quantity"],
                unit_price=engine_line["unit_price"],
                discount_amount=engine_line["discount_amount"],
                tax_id=raw_line.tax_id,
                tax_amount=engine_line["tax_amount"],
                line_total=engine_line["line_total"],
            )
            session.add(line)

        # 4. Add payments
        for p in payload.payments:
            payment = Payment(
                sale_id=sale.sale_id,
                org_id=sale.org_id,
                payment_method=p.payment_method,
                amount=p.amount,
                currency=p.currency,
                external_ref=p.external_ref,
                processed_at=p.processed_at,
            )
            session.add(payment)

        # 5. Commit + refresh
        await session.commit()
        await session.refresh(sale)

        # Load relationships
        _ = sale.sale_lines
        _ = sale.payments

        return sale

    # ---------------------------------------------------------
    # ARCHIVE SALE (SOFT DELETE VIA STATUS)
    # ---------------------------------------------------------
    async def archive_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
    ) -> Optional[Sale]:

        sale = await self.get_with_relations(session, sale_id)
        if not sale:
            return None

        # Soft delete
        sale.status = "archived"

        await session.commit()
        await session.refresh(sale)
        return sale


sales_service = SalesService()
