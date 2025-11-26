# backend/src/app/pos/services/checkout.py

from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.app.pos.schemas.pos_schemas import (
    SaleCreate,
    SaleLineCreate,
    PaymentCreate,
)

# FIXED IMPORTS
from src.app.inventory.models.item_models import Item
from src.app.pos.models.tax_rate_models import TaxRate


class CheckoutCalculator:
    """
    Pure calculation engine (Hybrid Mode).

    Responsibilities:
      - Validate sale line values
      - Auto-fill defaults from Item
      - Use TaxRate when available
      - Return pure calculation results (no DB access)
    """

    # -------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------
    def validate_line(self, line: SaleLineCreate, item: Item):
        if not line.item_id:
            raise ValueError("Sale line is missing required field: item_id")

        if not line.org_id:
            raise ValueError("Sale line is missing required field: org_id")

        # Quantity must be positive
        qty = Decimal(line.quantity)
        if qty <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Discount cannot be negative
        if line.discount_amount is not None and Decimal(line.discount_amount) < 0:
            raise ValueError("Discount amount cannot be negative")

        return True

    # -------------------------------------------------------
    # LINE CALCULATION
    # -------------------------------------------------------
    def calculate_line(
        self,
        line: SaleLineCreate,
        item: Item,
        tax_rate: Optional[TaxRate],
    ):
        """
        Hybrid calculation:
        - Defaults unit_price from Item if not supplied
        - Auto-use tax_rate if provided
        """

        qty = Decimal(line.quantity)
        price = (
            Decimal(line.unit_price)
            if line.unit_price is not None
            else Decimal(item.default_price)
        )
        discount = Decimal(line.discount_amount or 0)

        # Pre-tax amount
        line_subtotal = qty * price - discount
        if line_subtotal < 0:
            raise ValueError("Line subtotal cannot be negative (discount too large)")

        # Tax calculation
        if tax_rate:
            tax_amount = (line_subtotal * Decimal(tax_rate.rate_percent)) / Decimal("100")
        else:
            tax_amount = Decimal("0")

        line_total = line_subtotal + tax_amount

        return {
            "quantity": qty,
            "unit_price": price,
            "discount_amount": discount,
            "line_subtotal": line_subtotal,
            "tax_amount": tax_amount,
            "line_total": line_total,
        }

    # -------------------------------------------------------
    # SALE CALCULATION
    # -------------------------------------------------------
    def calculate_sale(
        self,
        sale: SaleCreate,
        items: List[Item],
        tax_rates: List[TaxRate],
    ):
        # Fast lookup maps
        item_map = {str(item.item_id): item for item in items}
        tax_map = {str(tax.tax_id): tax for tax in tax_rates}

        subtotal = Decimal("0")
        tax_total = Decimal("0")
        discount_total = Decimal("0")
        grand_total = Decimal("0")

        calculated_lines = []

        for line in sale.lines:
            item = item_map.get(str(line.item_id))
            if not item:
                raise ValueError(f"Item not found or not in this org: {line.item_id}")

            # Validate fields & rules
            self.validate_line(line, item)

            # Auto-fill tax_id from item if missing
            if line.tax_id is None:
                line.tax_id = item.tax_id

            # Resolve tax rate
            tax_rate = None
            if line.tax_id:
                tax_rate = tax_map.get(str(line.tax_id))
                if not tax_rate:
                    raise ValueError(f"Invalid tax rate: {line.tax_id}")

            # Perform calculation
            calc = self.calculate_line(line, item, tax_rate)

            subtotal += calc["line_subtotal"]
            tax_total += calc["tax_amount"]
            discount_total += calc["discount_amount"]
            grand_total += calc["line_total"]

            calculated_lines.append(calc)

        # Payments
        amount_paid = sum(Decimal(p.amount) for p in sale.payments)
        balance_due = grand_total - amount_paid

        return {
            "subtotal": subtotal,
            "tax_total": tax_total,
            "discount_total": discount_total,
            "grand_total": grand_total,
            "amount_paid": amount_paid,
            "balance_due": balance_due,
            "lines": calculated_lines,
        }


checkout_engine = CheckoutCalculator()
