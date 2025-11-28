# backend/src/app/pos/schemas/pos_schemas.py

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# CUSTOMERS
# ============================================================


class CustomerBase(BaseModel):
    org_id: UUID
    full_name: str
    external_ref: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    billing_address: Optional[dict] = None
    shipping_address: Optional[dict] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    external_ref: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    billing_address: Optional[dict] = None
    shipping_address: Optional[dict] = None
    notes: Optional[str] = None


class CustomerRead(CustomerBase):
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============================================================
# TERMINALS
# ============================================================


class TerminalBase(BaseModel):
    org_id: UUID
    name: str
    location_label: Optional[str] = None
    is_active: bool = True


class TerminalCreate(TerminalBase):
    pass


class TerminalUpdate(BaseModel):
    name: Optional[str] = None
    location_label: Optional[str] = None
    is_active: Optional[bool] = None


class TerminalRead(TerminalBase):
    terminal_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# TAX RATES
# ============================================================


class TaxRateBase(BaseModel):
    org_id: UUID
    name: str
    rate_percent: Decimal = Field(..., description="e.g. 8.25 for 8.25%")
    is_compound: bool = False
    is_default: bool = False


class TaxRateCreate(TaxRateBase):
    pass


class TaxRateUpdate(BaseModel):
    name: Optional[str] = None
    rate_percent: Optional[Decimal] = None
    is_compound: Optional[bool] = None
    is_default: Optional[bool] = None


class TaxRateRead(TaxRateBase):
    tax_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# SALE LINES
# ============================================================


class SaleLineBase(BaseModel):
    org_id: UUID
    item_id: UUID
    line_number: int
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_id: Optional[UUID] = None
    tax_amount: Decimal = Decimal("0")
    line_total: Decimal


class SaleLineCreate(SaleLineBase):
    pass


class SaleLineUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_id: Optional[UUID] = None
    tax_amount: Optional[Decimal] = None
    line_total: Optional[Decimal] = None


class SaleLineRead(SaleLineBase):
    sale_line_id: UUID
    sale_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# PAYMENTS
# ============================================================


class PaymentBase(BaseModel):
    org_id: UUID
    payment_method: str
    amount: Decimal
    currency: str = "USD"
    external_ref: Optional[str] = None
    processed_at: datetime


class PaymentCreate(PaymentBase):
    sale_id: UUID


class PaymentUpdate(BaseModel):
    payment_method: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    external_ref: Optional[str] = None
    processed_at: Optional[datetime] = None


class PaymentRead(PaymentBase):
    payment_id: UUID
    sale_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# SALES
# ============================================================


class SaleBase(BaseModel):
    org_id: UUID
    terminal_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    sale_number: Optional[str] = None
    status: str
    sale_type: str = "pos"
    subtotal: Decimal = Decimal("0")
    tax_total: Decimal = Decimal("0")
    discount_total: Decimal = Decimal("0")
    grand_total: Decimal = Decimal("0")
    amount_paid: Decimal = Decimal("0")
    balance_due: Decimal = Decimal("0")
    sale_date: datetime
    notes: Optional[str] = None
    created_by: Optional[UUID] = None


class SaleCreate(SaleBase):
    lines: List[SaleLineCreate]
    payments: List[PaymentCreate] = []


# ============================================================
# SALE UPDATE (PATCH)
# ============================================================


class SaleUpdate(BaseModel):
    # PATCH-able fields
    terminal_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    status: Optional[str] = None
    sale_type: Optional[str] = None
    sale_date: Optional[datetime] = None
    notes: Optional[str] = None

    # Optional children
    lines: Optional[List[SaleLineCreate]] = None
    payments: Optional[List[PaymentCreate]] = None

    model_config = {"from_attributes": True}

    # ---------------------------------------------------------
    # Convert PATCH → full recalculation payload
    # ---------------------------------------------------------
    def to_recalculate_payload(self, existing_sale):
        """
        Takes the partial PATCH fields and merges them with the existing
        sale to produce a full SaleCreate-like structure for use by
        checkout_service.calculate().
        """

        # Merge top-level sale info
        merged = {
            "org_id": existing_sale.org_id,
            "terminal_id": self.terminal_id or existing_sale.terminal_id,
            "customer_id": self.customer_id or existing_sale.customer_id,
            "sale_number": existing_sale.sale_number,  # Not overridden here
            "status": self.status or existing_sale.status,
            "sale_type": self.sale_type or existing_sale.sale_type,
            "sale_date": self.sale_date or existing_sale.sale_date,
            "notes": self.notes or existing_sale.notes,
            "created_by": existing_sale.created_by,
        }

        # Merge sale lines
        if self.lines is not None:
            merged_lines = self.lines
        else:
            merged_lines = [
                SaleLineCreate(
                    item_id=line.item_id,
                    line_number=line.line_number,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    discount_amount=line.discount_amount,
                    tax_id=line.tax_id,
                    tax_amount=line.tax_amount,
                    line_total=line.line_total,
                )
                for line in existing_sale.sale_lines
            ]

        # Merge payments
        if self.payments is not None:
            merged_payments = self.payments
        else:
            merged_payments = [
                PaymentCreate(
                    org_id=payment.org_id,
                    payment_method=payment.payment_method,
                    amount=payment.amount,
                    currency=payment.currency,
                    external_ref=payment.external_ref,
                    processed_at=payment.processed_at,
                    sale_id=existing_sale.sale_id,
                )
                for payment in existing_sale.payments
            ]

        merged["lines"] = merged_lines
        merged["payments"] = merged_payments

        return SaleCreate(**merged)


# ============================================================
# SALE READ MODELS
# ============================================================


class SaleRead(SaleBase):
    sale_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SaleReadWithLinesAndPayments(SaleRead):
    lines: List[SaleLineRead] = []
    payments: List[PaymentRead] = []

    model_config = {"from_attributes": True}
