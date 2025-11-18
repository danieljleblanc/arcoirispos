from __future__ import annotations

from enum import Enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Text, UniqueConstraint, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    cashier = "cashier"


class UserOrgRole(Base):
    __tablename__ = "user_org_roles"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", "role"),
        {"schema": "core"},
    )

    user_org_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.user_id"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="user_org_roles",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_org_roles",
    )
