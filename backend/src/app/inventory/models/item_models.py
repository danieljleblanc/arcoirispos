# backend/src/app/inventory/models/item_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base
from src.app.pos.models.tax_rate_models import TaxRate


class Item(Base):
    __tablename__ = "items"
    __table_args__ = {"schema": "inv"}

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )

    sku: Mapped[Optional[str]] = mapped_column(Text)
    barcode: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    item_type: Mapped[str] = mapped_column(Text, nullable=False)

    default_price: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )

    cost_basis: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 4))

    # ✔ FK now points to POS tax_rates
    tax_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.tax_rates.tax_id"),
        nullable=True,
    )

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

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="items",
    )

    # ✔ Correct one-way relationship to POS TaxRate
    tax_rate: Mapped["TaxRate"] = relationship("TaxRate", back_populates="items")

    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="item",
    )

    stock_levels: Mapped[List["StockLevel"]] = relationship(
        "StockLevel",
        back_populates="item",
    )

    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="item",
    )
