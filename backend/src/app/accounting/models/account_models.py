# backend/src/app/accounting/models/account_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

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


class ChartOfAccount(Base):
    __tablename__ = "chart_of_accounts"
    __table_args__ = (
        UniqueConstraint("org_id", "code"),
        {"schema": "acct"},
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    # Examples: asset, liability, equity, income, expense
    type: Mapped[str] = mapped_column(Text, nullable=False)
    subtype: Mapped[Optional[str]] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )

    # Self-referencing parent account
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acct.chart_of_accounts.account_id"),
        nullable=True,
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
    # Relationships
    # ------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="chart_of_accounts",
    )

    # Self-referencing parent/child relationships
    parent: Mapped[Optional["ChartOfAccount"]] = relationship(
        "ChartOfAccount",
        remote_side=lambda: ChartOfAccount.account_id,
        back_populates="children",
    )

    children: Mapped[List["ChartOfAccount"]] = relationship(
        "ChartOfAccount",
        back_populates="parent",
    )

    journal_lines: Mapped[List["JournalLine"]] = relationship(
        "JournalLine",
        back_populates="account",
        cascade="all, delete-orphan",
    )
