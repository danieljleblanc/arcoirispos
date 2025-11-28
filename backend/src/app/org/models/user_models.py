# backend/src/app/org/models/user_models.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "core"}

    # ----------------------------------------------------------------------
    # Columns
    # ----------------------------------------------------------------------
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(
        CITEXT, 
        nullable=False, 
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    display_name: Mapped[Optional[str]] = mapped_column(Text)

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

    # ----------------------------------------------------------------------
    # Relationships — all use clean forward_ref strings
    # ----------------------------------------------------------------------

    # Many-to-many between users and organizations through UserOrgRole
    user_org_roles: Mapped[List["UserOrgRole"]] = relationship(
        "UserOrgRole",
        back_populates="user",
    )

    # POS sales created by this user
    sales_created: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="created_by_user",
    )

    # Accounting journal entries created by this user
    journal_entries_created: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="created_by_user",
    )
