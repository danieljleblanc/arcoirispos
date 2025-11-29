# backend/src/app/org/models/organization_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": "core"}

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(Text)
    display_name: Mapped[Optional[str]] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------

    # Auth / org membership
    user_org_roles: Mapped[List["UserOrgRole"]] = relationship(
        "UserOrgRole",
        back_populates="organization",
    )
    
    # Accounting Relationships
    chart_of_accounts: Mapped[list["ChartOfAccount"]] = relationship(
    "ChartOfAccount",
    back_populates="organization",
    cascade="all, delete-orphan",
    )
    
    journal_entries: Mapped[List["JournalEntry"]] = relationship(
    "JournalEntry",
    back_populates="organization",
    cascade="all, delete-orphan",
    )

    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    customer_balances: Mapped[List["CustomerBalance"]] = relationship(
        "CustomerBalance",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    # POS relationships
    customers: Mapped[List["Customer"]] = relationship(
        "Customer",
        back_populates="organization",
    )

    sales: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="organization",
    )

    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="organization",
    )

    tax_rates: Mapped[List["TaxRate"]] = relationship(
        "TaxRate",
        back_populates="organization",
    )

    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="organization",
    )

    terminals: Mapped[List["Terminal"]] = relationship(
        "Terminal",
        back_populates="organization",
    )

    # Inventory relationships
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="organization",
    )

    locations: Mapped[List["Location"]] = relationship(
        "Location",
        back_populates="organization",
    )

    stock_levels: Mapped[List["StockLevel"]] = relationship(
        "StockLevel",
        back_populates="organization",
    )

    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="organization",
    )

