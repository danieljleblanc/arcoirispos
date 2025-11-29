# backend/src/app/accounting/models/bank_account_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    __table_args__ = (
        UniqueConstraint("org_id", "account_id"),
        {"schema": "acct"},
    )

    bank_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acct.chart_of_accounts.account_id"),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    institution: Mapped[Optional[str]] = mapped_column(Text)
    last4: Mapped[Optional[str]] = mapped_column(Text)

    currency: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'USD'"),
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

    # ------------------------------------------------------
    # CORRECT Relationships (ONLY these)
    # ------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
    )

    account: Mapped["ChartOfAccount"] = relationship(
        "ChartOfAccount", 
    )
