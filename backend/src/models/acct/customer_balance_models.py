from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

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

from src.models.base import Base


class CustomerBalance(Base):
    __tablename__ = "customer_balances"
    __table_args__ = (
        UniqueConstraint("org_id", "customer_id", "account_id"),
        {"schema": "acct"},
    )

    customer_balance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.customers.customer_id"),
        nullable=False,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acct.chart_of_accounts.account_id"),
        nullable=False,
    )
    balance: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        server_default=text("0"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="customer_balances",
    )
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="customer_balances",
    )
    account: Mapped["ChartOfAccount"] = relationship(
        "ChartOfAccount",
        back_populates="customer_balances",
    )
