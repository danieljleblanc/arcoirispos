# backend/src/app/inventory/models/stock_movement_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

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


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = {"schema": "inv"}

    movement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv.items.item_id"),
        nullable=False,
    )

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv.locations.location_id"),
        nullable=False,
    )

    # Optional link to the StockLevel snapshot this movement affects
    stock_level_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv.stock_levels.stock_level_id"),
        nullable=True,
    )

    source_type: Mapped[str] = mapped_column(Text, nullable=False)

    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
    )

    quantity_delta: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    unit_cost: Mapped[Optional[Numeric]] = mapped_column(
        Numeric(18, 4),
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # -------------------------
    # Relationships
    # -------------------------
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="stock_movements",
    )

    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="stock_movements",
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="stock_movements",
    )

    stock_level: Mapped[Optional["StockLevel"]] = relationship(
        "StockLevel",
        back_populates="stock_movements",
    )
