# backend/src/app/org/models/organization_settings_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum,
    Numeric,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base


# ------------------------------------------------------
# ENUMS
# ------------------------------------------------------

ROUNDING_MODES = (
    "none",
    "nickel",
    "dime",
    "quarter",
    "dollar",
)

INVENTORY_MODES = (
    "deduct_on_cart",
    "deduct_on_sale",
)

ROUNDING_TARGETS = (
    "none",
    "cash_only",
    "all_payments",
)


class OrganizationSettings(Base):
    __tablename__ = "organization_settings"
    __table_args__ = {"schema": "core"}

    settings_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # -----------------------------
    # Rounding configuration
    # -----------------------------
    rounding_mode: Mapped[str] = mapped_column(
        Enum(*ROUNDING_MODES, name="rounding_mode"),
        nullable=False,
        server_default=text("'none'"),
    )

    rounding_apply_to: Mapped[str] = mapped_column(
        Enum(*ROUNDING_TARGETS, name="rounding_targets"),
        nullable=False,
        server_default=text("'cash_only'"),
    )

    # -----------------------------
    # Inventory behavior
    # -----------------------------
    inventory_mode: Mapped[str] = mapped_column(
        Enum(*INVENTORY_MODES, name="inventory_mode"),
        nullable=False,
        server_default=text("'deduct_on_cart'"),
    )

    # Future:
    # receipt_footer
    # timezone
    # currency_symbol
    # default_tax_id
    # allow_suspended_orders

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

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="settings",
        lazy="joined",
    )
