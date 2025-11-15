from pydantic import BaseModel
from typing import List

class PurchaseOrderLineCreate(BaseModel):
    item_id: int
    quantity: int
    cost: float

class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    lines: List[PurchaseOrderLineCreate]

class PurchaseOrderLineOut(BaseModel):
    id: int
    item_id: int
    quantity: int
    cost: float

    class Config:
        from_attributes = True

class PurchaseOrderOut(BaseModel):
    id: int
    vendor_id: int
    status: str
    lines: List[PurchaseOrderLineOut]

    class Config:
        from_attributes = True
