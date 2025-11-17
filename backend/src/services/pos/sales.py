# backend/src/services/pos/sales.py

from typing import List, Optional
from uuid import UUID

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
    # GET SINGLE SALE + RELATIONS  (EXCLUDES ARCHIVED)
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
    # CREATE SALE (USES CHECKOUT ENGINE)
    # ---------------------------------------------------------
    async def create_sale(
        self,
        session: AsyncSession,
        payload: SaleCreate,
    ) -> Sale:

        # 1. Let the engine compute totals
        calc = await checkout_service.calculate(session, payload)

        # 2. Create Sale header
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
        await session.flush()   # ensures sale_id

        # 3. Create SaleLines
        for raw_in, calc_out in zip(payload.lines, calc["lines"]):
            line = SaleLine(
                sale_id=sale.sale_id,
                org_id=sale.org_id,
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

        # 4. Create Payments
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

        # 5. Finalize
        await session.commit()
        await session.refresh(sale)

        # Load relations
        _ = sale.sale_lines
        _ = sale.payments

        return sale
        
    # ---------------------------------------------------------
    # UPDATE SALE (PATCH)
    # ---------------------------------------------------------
    async def update_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
        payload,   # expects SaleUpdate
    ) -> Optional[Sale]:

        # 1. Load existing sale + relations
        existing_sale = await self.get_with_relations(session, sale_id)
        if not existing_sale:
            return None

        # Optional: block updates to archived sales
        if existing_sale.status == "archived":
            return None

        # 2. Convert SaleUpdate → complete recalculation payload
        full_payload = payload.to_recalculate_payload(existing_sale)

        # 3. Run checkout engine on merged content
        calc = await checkout_service.calculate(session, full_payload)

        # -----------------------------------------------------
        # 4. Update top-level fields
        # -----------------------------------------------------
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

        # -----------------------------------------------------
        # 5. Replace sale lines
        # -----------------------------------------------------
        for line in list(existing_sale.sale_lines):
            await session.delete(line)

        for raw_line, engine_line in zip(full_payload.lines, calc["lines"]):
            session.add(SaleLine(
                sale_id=existing_sale.sale_id,
                org_id=existing_sale.org_id,
                item_id=raw_line.item_id,
                line_number=raw_line.line_number,
                description=raw_line.description,
                quantity=engine_line["quantity"],
                unit_price=engine_line["unit_price"],
                discount_amount=engine_line["discount_amount"],
                tax_id=raw_line.tax_id,
                tax_amount=engine_line["tax_amount"],
                line_total=engine_line["line_total"],
            ))

        # -----------------------------------------------------
        # 6. Replace payments
        # -----------------------------------------------------
        for payment in list(existing_sale.payments):
            await session.delete(payment)

        for p in full_payload.payments:
            session.add(Payment(
                sale_id=existing_sale.sale_id,
                org_id=existing_sale.org_id,
                payment_method=p.payment_method,
                amount=p.amount,
                currency=p.currency,
                external_ref=p.external_ref,
                processed_at=p.processed_at,
            ))

        # -----------------------------------------------------
        # 7. Commit + reload
        # -----------------------------------------------------
        await session.commit()
        await session.refresh(existing_sale)

        _ = existing_sale.sale_lines
        _ = existing_sale.payments

        return existing_sale


    # ---------------------------------------------------------
    # ARCHIVE SALE (SOFT DELETE)
    # ---------------------------------------------------------
    async def archive_sale(
        self,
        session: AsyncSession,
        sale_id: UUID,
    ) -> Optional[Sale]:

        sale = await self.get_with_relations(session, sale_id)
        if not sale:
            return None

        sale.status = "archived"

        await session.commit()
        await session.refresh(sale)
        return sale


sales_service = SalesService()
