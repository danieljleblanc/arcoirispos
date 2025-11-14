from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class StockLevel(Base):
    __tablename__ = "stock_levels"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    location_id = Column(Integer, index=True)  # future multi-store support

    quantity = Column(Integer, nullable=False, default=0)

    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="stock_levels")
