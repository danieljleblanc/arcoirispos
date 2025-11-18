from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = {"schema": "pos"}

    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    terminal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.terminals.terminal_id"),
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.customers.customer_id"),
    )
    sale_number: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    sale_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pos'"),
    )
    subtotal: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    tax_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    discount_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    grand_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    amount_paid: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    balance_due: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    sale_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.user_id"),
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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="sales",
    )
    terminal: Mapped[Optional["Terminal"]] = relationship(
        "Terminal",
        back_populates="sales",
    )
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer",
        back_populates="sales",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="sales_created",
    )

    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="sale",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="sale",
        cascade="all, delete-orphan",
    )


class SaleLine(Base):
    __tablename__ = "sale_lines"
    __table_args__ = (
        UniqueConstraint("sale_id", "line_number"),
        {"schema": "pos"},
    )

    sale_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.sales.sale_id", ondelete="CASCADE"),
        nullable=False,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv.items.item_id"),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    quantity: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    discount_amount: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    tax_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.tax_rates.tax_id"),
    )
    tax_amount: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    line_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="sale_lines",
    )
    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="sale_lines",
    )
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="sale_lines",
    )
    tax_rate: Mapped[Optional["TaxRate"]] = relationship(
        "TaxRate",
        back_populates="sale_lines",
    )
