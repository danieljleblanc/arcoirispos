from __future__ import annotations
from enum import Enum

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT, JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass

class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    cashier = "cashier"
    
# ---------------------------------------------------------------------------
# ENUM TYPE (already created in DB)
# ---------------------------------------------------------------------------

acct_entry_type_enum = postgresql.ENUM(
    "debit",
    "credit",
    name="acct_entry_type",
    create_type=False,  # enum already exists via SQL
)


# ======================================================================
# CORE SCHEMA
# ======================================================================

class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": "core"}

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'UTC'"))
    base_currency: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'USD'"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user_org_roles: Mapped[List["UserOrgRole"]] = relationship(
        "UserOrgRole",
        back_populates="organization",
    )

    terminals: Mapped[List["Terminal"]] = relationship(
        "Terminal",
        back_populates="organization",
    )
    customers: Mapped[List["Customer"]] = relationship(
        "Customer",
        back_populates="organization",
    )
    tax_rates: Mapped[List["TaxRate"]] = relationship(
        "TaxRate",
        back_populates="organization",
    )

    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="organization",
    )
    locations: Mapped[List["Location"]] = relationship(
        "Location",
        back_populates="organization",
    )
    stock_levels: Mapped[List["StockLevel"]] = relationship(
        "StockLevel",
        back_populates="organization",
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="organization",
    )

    sales: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="organization",
    )
    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="organization",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="organization",
    )

    accounts: Mapped[List["ChartOfAccount"]] = relationship(
        "ChartOfAccount",
        back_populates="organization",
    )
    journal_entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="organization",
    )
    journal_lines: Mapped[List["JournalLine"]] = relationship(
        "JournalLine",
        back_populates="organization",
    )
    customer_balances: Mapped[List["CustomerBalance"]] = relationship(
        "CustomerBalance",
        back_populates="organization",
    )
    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="organization",
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "core"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    user_org_roles: Mapped[List["UserOrgRole"]] = relationship(
        "UserOrgRole",
        back_populates="user",
    )
    sales_created: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="created_by_user",
    )
    journal_entries_created: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="created_by_user",
    )


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
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
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


# ======================================================================
# POS SCHEMA
# ======================================================================

class Terminal(Base):
    __tablename__ = "terminals"
    __table_args__ = {"schema": "pos"}

    terminal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    location_label: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="terminals",
    )
    sales: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="terminal",
    )


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "pos"}

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    external_ref: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(CITEXT)
    phone: Mapped[Optional[str]] = mapped_column(Text)
    billing_address: Mapped[Optional[dict]] = mapped_column(JSONB)
    shipping_address: Mapped[Optional[dict]] = mapped_column(JSONB)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="customers",
    )
    sales: Mapped[List["Sale"]] = relationship(
        "Sale",
        back_populates="customer",
    )
    customer_balances: Mapped[List["CustomerBalance"]] = relationship(
        "CustomerBalance",
        back_populates="customer",
    )


class TaxRate(Base):
    __tablename__ = "tax_rates"
    __table_args__ = {"schema": "pos"}

    tax_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    rate_percent: Mapped[Numeric] = mapped_column(Numeric(9, 4), nullable=False)
    is_compound: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="tax_rates",
    )
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="tax_rate",
    )
    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="tax_rate",
    )


# ======================================================================
# INVENTORY SCHEMA
# ======================================================================

class Item(Base):
    __tablename__ = "items"
    __table_args__ = {"schema": "inv"}

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    sku: Mapped[Optional[str]] = mapped_column(Text)
    barcode: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    item_type: Mapped[str] = mapped_column(Text, nullable=False)
    default_price: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    cost_basis: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 4))
    tax_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.tax_rates.tax_id"),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="items",
    )
    tax_rate: Mapped[Optional["TaxRate"]] = relationship(
        "TaxRate",
        back_populates="items",
    )
    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="item",
    )
    stock_levels: Mapped[List["StockLevel"]] = relationship(
        "StockLevel",
        back_populates="item",
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="item",
    )


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "inv"}

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="locations",
    )
    stock_levels: Mapped[List["StockLevel"]] = relationship(
        "StockLevel",
        back_populates="location",
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="location",
    )


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
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
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
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    quantity_delta: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    unit_cost: Mapped[Optional[Numeric]] = mapped_column(Numeric(18, 4))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
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


# ======================================================================
# POS SALES & PAYMENTS
# ======================================================================

class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = {"schema": "pos"}

    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    terminal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.terminals.terminal_id"),
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.customers.customer_id"),
    )
    sale_number: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    sale_type: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'pos'"))
    subtotal: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    tax_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    discount_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    grand_total: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    amount_paid: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    balance_due: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    sale_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.user_id"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="sales",
    )
    terminal: Mapped[Optional["Terminal"]] = relationship(
        "Terminal",
        back_populates="sales",
    )
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer",
        back_populates="sales",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="sales_created",
    )

    sale_lines: Mapped[List["SaleLine"]] = relationship(
        "SaleLine",
        back_populates="sale",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="sale",
        cascade="all, delete-orphan",
    )


class SaleLine(Base):
    __tablename__ = "sale_lines"
    __table_args__ = (
        UniqueConstraint("sale_id", "line_number"),
        {"schema": "pos"},
    )

    sale_line_id: Mapped[uuid.UUID] = mapped_column(
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
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv.items.item_id"),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    quantity: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    discount_amount: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    tax_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos.tax_rates.tax_id"),
    )
    tax_amount: Mapped[Numeric] = mapped_column(
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    line_total: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="sale_lines",
    )
    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="sale_lines",
    )
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="sale_lines",
    )
    tax_rate: Mapped[Optional["TaxRate"]] = relationship(
        "TaxRate",
        back_populates="sale_lines",
    )


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
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'USD'"))
    external_ref: Mapped[Optional[str]] = mapped_column(Text)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="payments",
    )
    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="payments",
    )


# ======================================================================
# ACCOUNTING SCHEMA
# ======================================================================

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
    type: Mapped[str] = mapped_column(Text, nullable=False)
    subtype: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acct.chart_of_accounts.account_id"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="accounts",
    )
    parent: Mapped[Optional["ChartOfAccount"]] = relationship(
        "ChartOfAccount",
        remote_side="ChartOfAccount.account_id",
        back_populates="children",
    )
    children: Mapped[List["ChartOfAccount"]] = relationship(
        "ChartOfAccount",
        back_populates="parent",
    )
    journal_lines: Mapped[List["JournalLine"]] = relationship(
        "JournalLine",
        back_populates="account",
    )
    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="account",
    )
    customer_balances: Mapped[List["CustomerBalance"]] = relationship(
        "CustomerBalance",
        back_populates="account",
    )


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = {"schema": "acct"}

    journal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organizations.org_id"),
        nullable=False,
    )
    journal_number: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[Optional[str]] = mapped_column(Text)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    description: Mapped[Optional[str]] = mapped_column(Text)
    journal_date: Mapped[date] = mapped_column(Date, nullable=False)
    posted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.user_id"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="journal_entries",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="journal_entries_created",
    )
    journal_lines: Mapped[List["JournalLine"]] = relationship(
        "JournalLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )


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
    entry_type: Mapped[str] = mapped_column(acct_entry_type_enum, nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(18, 4), nullable=False)
    memo: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    journal_entry: Mapped["JournalEntry"] = relationship(
        "JournalEntry",
        back_populates="journal_lines",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="journal_lines",
    )
    account: Mapped["ChartOfAccount"] = relationship(
        "ChartOfAccount",
        back_populates="journal_lines",
    )


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
        Numeric(18, 4), nullable=False, server_default=text("0")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
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
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'USD'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="bank_accounts",
    )
    account: Mapped["ChartOfAccount"] = relationship(
        "ChartOfAccount",
        back_populates="bank_accounts",
    )
