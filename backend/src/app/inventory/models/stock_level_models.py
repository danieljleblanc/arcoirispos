# backend/src/app/inventory/models/stock_level_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base


class StockLevel(Base):
    __tablename__ = "stock_levels"
    __table_args__ = (
        UniqueConstraint("org_id", "item_id", "location_id"),
        {"schema": "inv"},
    )

    stock_level_id: Mapped[uuid.UUID] = mapped_column(
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

    quantity_on_hand: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # -------------------------
    # Relationships
    # -------------------------
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="stock_levels",
    )

    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="stock_levels",
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="stock_levels",
    )

    # 🔥 REQUIRED reverse relationship to StockMovement
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="stock_level",
        cascade="all, delete-orphan",
    )
