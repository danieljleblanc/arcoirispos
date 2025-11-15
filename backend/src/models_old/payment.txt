from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)

    method = Column(String(50), nullable=False)  # cash, card, applepay, venmo, etc.
    amount = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sale = relationship("Sale", back_populates="payments")
