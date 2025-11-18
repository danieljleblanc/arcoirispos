from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    location_id = Column(Integer, index=True)

    quantity_change = Column(Integer, nullable=False)   # +5, -1, etc.
    transaction_type = Column(String(50), nullable=False)
    reference_id = Column(Integer, nullable=True)       # sale_id, po_id

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="inventory_transactions")
