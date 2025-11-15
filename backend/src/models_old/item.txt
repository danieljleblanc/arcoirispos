from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, index=True)

    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True, unique=True)
    description = Column(String(500), nullable=True)

    price = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sale_lines = relationship("SaleLine", back_populates="item")
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    cost = Column(Numeric(10,2), nullable=True)          # cost from vendor
    track_stock = Column(Boolean, default=True)
    reorder_point = Column(Integer, nullable=True)
    
    vendor = relationship("Vendor", back_populates="items")
    stock_levels = relationship("StockLevel", back_populates="item")
    inventory_transactions = relationship("InventoryTransaction", back_populates="item")
