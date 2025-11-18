from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import relationship
from .base import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    lines = relationship("SaleLine", back_populates="sale")
    payments = relationship("Payment", back_populates="sale")


class SaleLine(Base):
    __tablename__ = "sale_lines"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, nullable=False, default=1)
    line_total = Column(Numeric(10, 2), nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="lines")
    item = relationship("Item", back_populates="sale_lines")
