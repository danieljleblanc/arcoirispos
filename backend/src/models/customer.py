from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, index=True)  # Future multi-tenant support

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), nullable=True, unique=True)
    phone = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sales = relationship("Sale", back_populates="customer")
