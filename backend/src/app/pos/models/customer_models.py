# backend/src/app/pos/models/customer_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    Text,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT
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

    # -----------------------------
    # Identity
    # -----------------------------
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)

    email: Mapped[Optional[str]] = mapped_column(CITEXT)
    phone: Mapped[Optional[str]] = mapped_column(Text)

    # -----------------------------
    # Address
    # -----------------------------
    street_address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(Text)
    state: Mapped[Optional[str]] = mapped_column(Text)
    zip: Mapped[Optional[str]] = mapped_column(Text)

    # -----------------------------
    # Metadata
    # -----------------------------
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

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    last_edited_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    last_edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # -----------------------------
    # Relationships
    # -----------------------------
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
