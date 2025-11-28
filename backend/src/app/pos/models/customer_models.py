# backend/src/app/pos/models/customer_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "pos"}

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )

    external_ref: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(CITEXT)
    phone: Mapped[Optional[str]] = mapped_column(Text)

    billing_address: Mapped[Optional[dict]] = mapped_column(JSONB)
    shipping_address: Mapped[Optional[dict]] = mapped_column(JSONB)

    notes: Mapped[Optional[str]] = mapped_column(Text)

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

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="customers",
    )

    sales: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="customer",
    )

    customer_balances: Mapped[List["CustomerBalance"]] = relationship(
        "CustomerBalance",
        back_populates="customer",
    )
