"""seed initial data

Revision ID: 2864583ca021
Revises: 853113448960
Create Date: 2025-11-18 14:02:25.884289
"""
from typing import Sequence, Union
from uuid import uuid4
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = "2864583ca021"
down_revision: Union[str, Sequence[str], None] = "853113448960"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    org_id = str(uuid4())
    admin_user_id = str(uuid4())
    now = datetime.utcnow()

    # ------------------------------
    # Table objects
    # ------------------------------

    organizations = sa.table(
        "organizations",
        sa.column("org_id", sa.String),
        sa.column("name", sa.String),
        sa.column("legal_name", sa.String),
        sa.column("timezone", sa.String),
        sa.column("base_currency", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
        schema="core",
    )

    users = sa.table(
        "users",
        sa.column("user_id", sa.String),
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("display_name", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
        schema="core",
    )

    user_org_roles = sa.table(
        "user_org_roles",
        sa.column("user_org_role_id", sa.String),
        sa.column("org_id", sa.String),
        sa.column("user_id", sa.String),
        sa.column("role", sa.String),
        sa.column("is_primary", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        schema="core",
    )

    tax_rates = sa.table(
        "tax_rates",
        sa.column("tax_id", sa.String),
        sa.column("org_id", sa.String),
        sa.column("name", sa.String),
        sa.column("rate_percent", sa.Numeric),
        sa.column("is_compound", sa.Boolean),
        sa.column("is_default", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
        schema="pos",
    )

    # ------------------------------
    # Insert: organizations
    # ------------------------------

    op.bulk_insert(
        organizations,
        [
            {
                "org_id": org_id,
                "name": "Arcoiris POS",
                "legal_name": "Arcoiris POS",
                "timezone": "UTC",
                "base_currency": "USD",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    # ------------------------------
    # Insert: admin user
    # ------------------------------

    admin_password_hash = "$2b$12$Vnp0Po7yFgty6yfUQFpD5O6sf5ZCZiequD2GM1l4IQhmgbB7iaG.6"

    op.bulk_insert(
        users,
        [
            {
                "user_id": admin_user_id,
                "email": "admin@arcoirispos.com",
                "password_hash": admin_password_hash,
                "display_name": "System Administrator",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    # ------------------------------
    # Insert: user_org_roles
    # ------------------------------

    op.bulk_insert(
        user_org_roles,
        [
            {
                "user_org_role_id": str(uuid4()),
                "org_id": org_id,
                "user_id": admin_user_id,
                "role": "admin",
                "is_primary": True,
                "created_at": now,
            }
        ],
    )

    # ------------------------------
    # Insert: default tax rate
    # ------------------------------

    op.bulk_insert(
        tax_rates,
        [
            {
                "tax_id": str(uuid4()),
                "org_id": org_id,
                "name": "Default Sales Tax",
                "rate_percent": 0.0725,
                "is_compound": False,
                "is_default": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM pos.tax_rates WHERE name = 'Default Sales Tax'")
    op.execute("DELETE FROM core.user_org_roles WHERE role = 'admin'")
    op.execute("DELETE FROM core.users WHERE email = 'admin@arcoirispos.com'")
    op.execute("DELETE FROM core.organizations WHERE name = 'Arcoiris POS'")
