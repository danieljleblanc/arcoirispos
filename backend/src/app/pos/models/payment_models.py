# backend/src/app/pos/models/payment_models.py

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


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "pos"}

    payment_id: Mapped[uuid.UUID] = mapped_column(
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

    payment_method: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------
    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="payments",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="payments",
    )
