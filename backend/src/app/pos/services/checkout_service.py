# backend/src/app/pos/services/checkout_service.py

from typing import List
from uuid import UUID
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ✔ FIXED: Import only Item from inventory
from src.app.inventory.models.item_models import Item

# ✔ FIXED: Import TaxRate from POS where it actually exists
from src.app.pos.models.tax_rate_models import TaxRate

from src.app.pos.schemas.pos_schemas import (
    SaleCreate,
    SaleLineCreate,
    PaymentCreate,
)

# Placeholder — you can plug in real engine later
checkout_engine = None


class CheckoutService:
    """
    Service layer:
    - Pulls items/tax rates from DB
    - Validates sale input
    - Delegates all math to CheckoutCalculator
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    async def validate(self, session: AsyncSession, sale: SaleCreate):

        # Basic required fields
        if len(sale.lines) == 0:
            raise HTTPException(
                status_code=400,
                detail="A sale must contain at least one line."
            )

        # Collect item IDs + tax IDs
        item_ids = [line.item_id for line in sale.lines]
        tax_ids = [line.tax_id for line in sale.lines if line.tax_id is not None]

        # Load from DB
        db_items = await self.load_items(session, sale.org_id, item_ids)
        db_taxes = await self.load_tax_rates(session, sale.org_id, tax_ids)

        # ---- Validate Items ----
        db_item_map = {item.item_id: item for item in db_items}

        for line in sale.lines:
            if line.item_id not in db_item_map:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item not found: {line.item_id}"
                )
            if line.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than zero."
                )

        # ---- Validate Tax Rates ----
        db_tax_map = {tax.tax_id: tax for tax in db_taxes}

        for line in sale.lines:
            if line.tax_id and line.tax_id not in db_tax_map:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tax rate not found: {line.tax_id}"
                )

        # ---- Validate Payments ----
        total_payments = sum([p.amount for p in sale.payments])
        if total_payments < 0:
            raise HTTPException(
                status_code=400,
                detail="Payment amounts cannot be negative."
            )

        return True

    # ---------------------------------------------------------
    # LOADERS
    # ---------------------------------------------------------
    async def load_items(self, session: AsyncSession, org_id: UUID, item_ids: List[UUID]):
        if not item_ids:
            return []

        stmt = (
            select(Item)
            .where(Item.org_id == org_id)
            .where(Item.item_id.in_(item_ids))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def load_tax_rates(self, session: AsyncSession, org_id: UUID, tax_ids: List[UUID]):
        if not tax_ids:
            return []

        stmt = (
            select(TaxRate)
            .where(TaxRate.org_id == org_id)
            .where(TaxRate.tax_id.in_(tax_ids))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    # ---------------------------------------------------------
    # CALCULATION (DELEGATES TO checkout_engine)
    # ---------------------------------------------------------
    async def calculate(self, session: AsyncSession, sale: SaleCreate) -> dict:

        item_ids = [line.item_id for line in sale.lines]
        tax_ids = [line.tax_id for line in sale.lines if line.tax_id is not None]

        items = await self.load_items(session, sale.org_id, item_ids)
        tax_rates = await self.load_tax_rates(session, sale.org_id, tax_ids)

        if checkout_engine is None:
            raise HTTPException(
                status_code=500,
                detail="Checkout engine is not initialized."
            )

        return checkout_engine.calculate_sale(sale, items, tax_rates)


checkout_service = CheckoutService()
