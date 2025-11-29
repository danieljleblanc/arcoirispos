# backend/src/app/accounting/models/journal_line_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base
from src.app.accounting.models.enums import acct_entry_type_enum


class JournalLine(Base):
    __tablename__ = "journal_lines"
    __table_args__ = (
        UniqueConstraint("journal_id", "line_number"),
        CheckConstraint("amount > 0"),
        {"schema": "acct"},
    )

    journal_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    journal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acct.journal_entries.journal_id", ondelete="CASCADE"),
        nullable=False,
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )

    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acct.chart_of_accounts.account_id"),
        nullable=False,
    )

    entry_type: Mapped[str] = mapped_column(
        acct_entry_type_enum,
        nullable=False,
    )

    amount: Mapped[Numeric] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    memo: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------

    journal_entry: Mapped["JournalEntry"] = relationship(
        "JournalEntry",
        back_populates="journal_lines",
    )

    account: Mapped["ChartOfAccount"] = relationship(
        "ChartOfAccount",
        back_populates="journal_lines",
    )
