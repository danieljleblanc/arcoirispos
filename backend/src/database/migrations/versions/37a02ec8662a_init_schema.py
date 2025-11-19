"""init schema

Revision ID: 37a02ec8662a
Revises:
Create Date: 2025-11-18 00:52:52.732640
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers, used by Alembic.
revision = "37a02ec8662a"
down_revision: Union[str, Sequence[str], None] = "000000000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # Ensure schemas exist
    # ---------------------------------------------------------
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS acct")
    op.execute("CREATE SCHEMA IF NOT EXISTS inv")
    op.execute("CREATE SCHEMA IF NOT EXISTS pos")

    # ---------------------------------------------------------
    # Required Postgres extensions
    # ---------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")  # Needed for gen_random_uuid()

    # ---------------------------------------------------------
    # ENUM types
    # ---------------------------------------------------------
    acct_entry_type = postgresql.ENUM(
        "debit",
        "credit",
        name="acct_entry_type",
        schema="acct",
    )
    acct_entry_type.create(op.get_bind(), checkfirst=True)

    # ---------------------------------------------------------
    # Tables
    # ---------------------------------------------------------
    op.create_table(
        "organizations",
        sa.Column("org_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("legal_name", sa.Text(), nullable=True),
        sa.Column("timezone", sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
        sa.Column("base_currency", sa.Text(), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("org_id"),
        schema="core",
    )

    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        schema="core",
    )

    op.create_table(
        "chart_of_accounts",
        sa.Column("account_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("subtype", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["acct.chart_of_accounts.account_id"]),
        sa.PrimaryKeyConstraint("account_id"),
        sa.UniqueConstraint("org_id", "code"),
        schema="acct",
    )

    op.create_table(
        "journal_entries",
        sa.Column("journal_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("journal_number", sa.Text(), nullable=True),
        sa.Column("source_type", sa.Text(), nullable=True),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("journal_date", sa.Date(), nullable=False),
        sa.Column("posted", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["core.users.user_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("journal_id"),
        schema="acct",
    )

    op.create_table(
        "user_org_roles",
        sa.Column("user_org_role_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["core.users.user_id"]),
        sa.PrimaryKeyConstraint("user_org_role_id"),
        sa.UniqueConstraint("org_id", "user_id", "role"),
        schema="core",
    )

    op.create_table(
        "locations",
        sa.Column("location_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("code", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("location_id"),
        schema="inv",
    )

    op.create_table(
        "customers",
        sa.Column("customer_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("external_ref", sa.Text(), nullable=True),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=True),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("billing_address", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("shipping_address", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("customer_id"),
        schema="pos",
    )

    op.create_table(
        "tax_rates",
        sa.Column("tax_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("rate_percent", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("is_compound", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("tax_id"),
        schema="pos",
    )

    op.create_table(
        "terminals",
        sa.Column("terminal_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("location_label", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("terminal_id"),
        schema="pos",
    )

    op.create_table(
        "bank_accounts",
        sa.Column("bank_account_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("institution", sa.Text(), nullable=True),
        sa.Column("last4", sa.Text(), nullable=True),
        sa.Column("currency", sa.Text(), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["acct.chart_of_accounts.account_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("bank_account_id"),
        sa.UniqueConstraint("org_id", "account_id"),
        schema="acct",
    )

    op.create_table(
        "customer_balances",
        sa.Column("customer_balance_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("balance", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["acct.chart_of_accounts.account_id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["pos.customers.customer_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("customer_balance_id"),
        sa.UniqueConstraint("org_id", "customer_id", "account_id"),
        schema="acct",
    )

    op.create_table(
        "journal_lines",
        sa.Column("journal_line_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("journal_id", sa.UUID(), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column(
    "entry_type",
    postgresql.ENUM(
        "debit",
        "credit",
        name="acct_entry_type",
        schema="acct",
        create_type=False,
    ),
    nullable=False,
),

        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.CheckConstraint("amount > 0"),
        sa.ForeignKeyConstraint(["account_id"], ["acct.chart_of_accounts.account_id"]),
        sa.ForeignKeyConstraint(["journal_id"], ["acct.journal_entries.journal_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("journal_line_id"),
        sa.UniqueConstraint("journal_id", "line_number"),
        schema="acct",
    )

    op.create_table(
        "items",
        sa.Column("item_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("sku", sa.Text(), nullable=True),
        sa.Column("barcode", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("item_type", sa.Text(), nullable=False),
        sa.Column("default_price", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("cost_basis", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("tax_id", sa.UUID(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.ForeignKeyConstraint(["tax_id"], ["pos.tax_rates.tax_id"]),
        sa.PrimaryKeyConstraint("item_id"),
        schema="inv",
    )

    op.create_table(
        "sales",
        sa.Column("sale_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("terminal_id", sa.UUID(), nullable=True),
        sa.Column("customer_id", sa.UUID(), nullable=True),
        sa.Column("sale_number", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("sale_type", sa.Text(), server_default=sa.text("'pos'"), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("tax_total", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("discount_total", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("grand_total", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("amount_paid", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("balance_due", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("sale_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["core.users.user_id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["pos.customers.customer_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.ForeignKeyConstraint(["terminal_id"], ["pos.terminals.terminal_id"]),
        sa.PrimaryKeyConstraint("sale_id"),
        schema="pos",
    )

    op.create_table(
        "stock_levels",
        sa.Column("stock_level_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=False),
        sa.Column("location_id", sa.UUID(), nullable=False),
        sa.Column("quantity_on_hand", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["inv.items.item_id"]),
        sa.ForeignKeyConstraint(["location_id"], ["inv.locations.location_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("stock_level_id"),
        sa.UniqueConstraint("org_id", "item_id", "location_id"),
        schema="inv",
    )

    op.create_table(
        "stock_movements",
        sa.Column("movement_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=False),
        sa.Column("location_id", sa.UUID(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("quantity_delta", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["inv.items.item_id"]),
        sa.ForeignKeyConstraint(["location_id"], ["inv.locations.location_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.PrimaryKeyConstraint("movement_id"),
        schema="inv",
    )

    op.create_table(
        "payments",
        sa.Column("payment_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("sale_id", sa.UUID(), nullable=False),
        sa.Column("payment_method", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("currency", sa.Text(), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("external_ref", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["pos.sales.sale_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("payment_id"),
        schema="pos",
    )

    op.create_table(
        "sale_lines",
        sa.Column("sale_line_id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("sale_id", sa.UUID(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("discount_amount", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("tax_id", sa.UUID(), nullable=True),
        sa.Column("tax_amount", sa.Numeric(precision=18, scale=4), server_default=sa.text("0"), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["inv.items.item_id"]),
        sa.ForeignKeyConstraint(["org_id"], ["core.organizations.org_id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["pos.sales.sale_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tax_id"], ["pos.tax_rates.tax_id"]),
        sa.PrimaryKeyConstraint("sale_line_id"),
        sa.UniqueConstraint("sale_id", "line_number"),
        schema="pos",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("sale_lines", schema="pos")
    op.drop_table("payments", schema="pos")
    op.drop_table("stock_movements", schema="inv")
    op.drop_table("stock_levels", schema="inv")
    op.drop_table("sales", schema="pos")
    op.drop_table("items", schema="inv")
    op.drop_table("journal_lines", schema="acct")
    op.drop_table("customer_balances", schema="acct")
    op.drop_table("bank_accounts", schema="acct")
    op.drop_table("terminals", schema="pos")
    op.drop_table("tax_rates", schema="pos")
    op.drop_table("customers", schema="pos")
    op.drop_table("locations", schema="inv")
    op.drop_table("user_org_roles", schema="core")
    op.drop_table("journal_entries", schema="acct")
    op.drop_table("chart_of_accounts", schema="acct")
    op.drop_table("users", schema="core")
    op.drop_table("organizations", schema="core")

    # Drop ENUM last
    op.execute("DROP TYPE IF EXISTS acct.acct_entry_type CASCADE")
