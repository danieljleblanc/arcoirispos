from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


# ─────────────────────────────────────────────
# SALE LINE SCHEMAS
# ─────────────────────────────────────────────
class SaleLineCreate(BaseModel):
    item_id: int
    quantity: int


class SaleLineOut(BaseModel):
    id: int
    item_id: int
    quantity: int
    line_total: Decimal

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PAYMENT SCHEMAS
# ─────────────────────────────────────────────
class PaymentCreate(BaseModel):
    method: str
    amount: Decimal


class PaymentOut(BaseModel):
    id: int
    method: str
    amount: Decimal

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# SALE SCHEMAS
# ─────────────────────────────────────────────
class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    lines: Optional[List[SaleLineCreate]] = []


class SaleOut(BaseModel):
    id: int
    customer_id: Optional[int]
    total_amount: Decimal
    lines: List[SaleLineOut] = []
    payments: List[PaymentOut] = []

    class Config:
        from_attributes = True
