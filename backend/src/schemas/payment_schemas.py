from pydantic import BaseModel
from decimal import Decimal


class PaymentCreate(BaseModel):
    method: str
    amount: Decimal


class PaymentOut(BaseModel):
    id: int
    method: str
    amount: Decimal

    class Config:
        from_attributes = True
