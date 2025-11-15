from pydantic import BaseModel

class StockLevelOut(BaseModel):
    item_id: int
    location_id: int
    quantity: int

    class Config:
        from_attributes = True
