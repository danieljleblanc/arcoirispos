from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, Numeric, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class TaxRate(Base):
    __tablename__ = "tax_rates"
    __table_args__ = {"schema": "pos"}

    tax_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    rate_percent: Mapped[Numeric] = mapped_column(
        Numeric(9, 4),
        nullable=False,
    )
    is_compound: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
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

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="tax_rates",
    )
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="tax_rate",
    )
    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="tax_rate",
    )
