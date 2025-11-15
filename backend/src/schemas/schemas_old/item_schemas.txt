from pydantic import BaseModel
from decimal import Decimal


class ItemCreate(BaseModel):
    name: str
    sku: str | None = None
    description: str | None = None
    price: Decimal


class ItemOut(BaseModel):
    id: int
    name: str
    sku: str | None
    description: str | None
    price: Decimal

    class Config:
        from_attributes = True
