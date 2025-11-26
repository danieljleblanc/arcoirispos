# backend/src/app/pos/services/sales.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.base_repository import BaseRepository
from src.app.pos.models.sale_models import Sale, SaleLine
from src.app.pos.models.payment_models import Payment
from src.app.pos.schemas.pos_schemas import SaleCreate

# ✔️ Corrected import
from src.app.pos.services.checkout_service import checkout_service


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
            .where(
                Sale.org_id == org_id,
                Sale.status != "archived"
            )
            .order_by(Sale.sale_date.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

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
            .where(
                Sale.sale_id == sale_id,
                Sale.status != "archived"
            )
        )

        result = await session.execute(stmt)
        sale = result.scalar_one_or_none()

        if sale:
            _ = sale.sale_lines
            _ = sale.payments

        return sale

    # ---------------------------------------------------------
    # CREATE SALE — uses checkout engine
    # ---------------------------------------------------------
    async def create_sale(
        self,
        session: AsyncSession,
        payload: SaleCreate,
        *,
        org_id: UUID,
    ) -> Sale:

        # Let engine calculate totals
        calc = await checkout_service.calculate(session, payload)

        sale = Sale(
            org_id=org_id,
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
        await session.flush()

        # Sale lines
        for raw_in, calc_out in zip(payload.lines, calc["lines"]):
            line = SaleLine(
                sale_id=sale.sale_id,
                org_id=org_id,
                item_id=raw_in.item_id,
                line_number=raw_in.line_number,
                description=raw_in.description,
                quantity=calc_out["quantity"],
                unit_price=calc_out["unit_price"],
                discount_amount=calc_out["discount_amount"],
                tax_id=raw_in.tax_id,
                tax_amount=calc_out["tax_amount"],
                line_total=calc_out["line_total"],
            )
            session.add(line)

        # Payments
        for p in payload.payments:
            pay = Payment(
                sale_id=sale.sale_id,
                org_id=org_id,
                payment_method=p.payment_method,
                amount=p.amount,
                currency=p.currency,
                external_ref=p.external_ref,
                processed_at=p.processed_at,
            )
            session.add(pay)

        await session.commit()
        await session.refresh(sale)

        _ = sale.sale_lines
        _ = sale.payments

        return sale

    # ---------------------------------------------------------
    # UPDATE SALE (PATCH + RECALC)
    # ---------------------------------------------------------
    async def update_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
        payload,
        *,
        org_id: UUID,
    ) -> Optional[Sale]:

        existing_sale = await self.get_with_relations(session, sale_id)
        if not existing_sale or existing_sale.status == "archived":
            return None

        full_payload = payload.to_recalculate_payload(existing_sale)
        calc = await checkout_service.calculate(session, full_payload)

        # Top-level updates
        existing_sale.terminal_id = full_payload.terminal_id
        existing_sale.customer_id = full_payload.customer_id
        existing_sale.status      = full_payload.status
        existing_sale.sale_type   = full_payload.sale_type
        existing_sale.sale_date   = full_payload.sale_date
        existing_sale.notes       = full_payload.notes

        # Totals
        existing_sale.subtotal       = calc["subtotal"]
        existing_sale.tax_total      = calc["tax_total"]
        existing_sale.discount_total = calc["discount_total"]
        existing_sale.grand_total    = calc["grand_total"]
        existing_sale.amount_paid    = calc["amount_paid"]
        existing_sale.balance_due    = calc["balance_due"]

        # Replace sale lines
        for line in list(existing_sale.sale_lines):
            await session.delete(line)

        for raw, eng in zip(full_payload.lines, calc["lines"]):
            session.add(SaleLine(
                sale_id=existing_sale.sale_id,
                org_id=org_id,
                item_id=raw.item_id,
                line_number=raw.line_number,
                description=raw.description,
                quantity=eng["quantity"],
                unit_price=eng["unit_price"],
                discount_amount=eng["discount_amount"],
                tax_id=raw.tax_id,
                tax_amount=eng["tax_amount"],
                line_total=eng["line_total"],
            ))

        # Replace payments
        for p in list(existing_sale.payments):
            await session.delete(p)

        for p in full_payload.payments:
            session.add(Payment(
                sale_id=existing_sale.sale_id,
                org_id=org_id,
                payment_method=p.payment_method,
                amount=p.amount,
                currency=p.currency,
                external_ref=p.external_ref,
                processed_at=p.processed_at,
            ))

        await session.commit()
        await session.refresh(existing_sale)

        _ = existing_sale.sale_lines
        _ = existing_sale.payments

        return existing_sale

    # ---------------------------------------------------------
    # ARCHIVE SALE
    # ---------------------------------------------------------
    async def archive_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
        *,
        org_id: UUID,
    ) -> Optional[Sale]:

        sale = await self.get_with_relations(session, sale_id)
        if not sale or sale.org_id != org_id:
            return None

        sale.status = "archived"

        await session.commit()
        await session.refresh(sale)
        return sale


sales_service = SalesService()
