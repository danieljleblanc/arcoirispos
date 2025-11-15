# backend/src/schemas/pos_schemas.py

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# -------- Customers --------

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

    class Config:
        orm_mode = True


# -------- Terminals --------

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

    class Config:
        orm_mode = True


# -------- Tax Rates --------

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

    class Config:
        orm_mode = True


# -------- Sale Lines --------

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


class SaleLineRead(SaleLineBase):
    sale_line_id: UUID
    sale_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Payments --------

class PaymentBase(BaseModel):
    org_id: UUID
    payment_method: str
    amount: Decimal
    currency: str = "USD"
    external_ref: Optional[str] = None
    processed_at: datetime


class PaymentCreate(PaymentBase):
    sale_id: UUID


class PaymentRead(PaymentBase):
    payment_id: UUID
    sale_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Sales --------

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


class SaleUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class SaleRead(SaleBase):
    sale_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SaleReadWithLinesAndPayments(SaleRead):
    lines: List[SaleLineRead] = []
    payments: List[PaymentRead] = []
