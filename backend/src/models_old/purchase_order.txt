from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    organization_id = Column(Integer, index=True)

    status = Column(String(50), default="open")  # open, received, canceled

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    received_at = Column(DateTime(timezone=True), nullable=True)

    vendor = relationship("Vendor", back_populates="purchase_orders")
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order")
