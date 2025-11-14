from pydantic import BaseModel

class InventoryTransactionOut(BaseModel):
    id: int
    item_id: int
    quantity_change: int
    transaction_type: str
    reference_id: int | None

    class Config:
        from_attributes = True
