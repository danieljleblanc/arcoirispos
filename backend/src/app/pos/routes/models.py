# backend/src/app/pos/routes/models.py

from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------
# Minimal placeholder DTOs used by api_router imports
# ---------------------------------------------------------------

class SaleSummary(BaseModel):
    sale_id: UUID
    sale_number: Optional[str]
    grand_total: float
    created_at: datetime


class CustomerSummary(BaseModel):
    customer_id: UUID
    full_name: str
    email: Optional[str]


class PaymentSummary(BaseModel):
    payment_id: UUID
    amount: float
    payment_method: str
    created_at: datetime
