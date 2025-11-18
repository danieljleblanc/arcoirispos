"""seed initial data

Revision ID: <your_rev>
Revises: 37a02ec8662a
Create Date: 2025-11-18

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "<your_rev>"
down_revision: Union[str, Sequence[str], None] = "37a02ec8662a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Insert baseline system data.
    Safe to run on a fresh database without duplicates.
    """

    # ---------------------------------------------
    # Create a default organization
    # ---------------------------------------------
    op.execute("""
        INSERT INTO core.organizations (
            org_id, name, legal_name, timezone, base_currency,
            is_active, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(),
            'Default Organization',
            'Default Organization LLC',
            'UTC',
            'USD',
            TRUE,
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
    """)

    # ---------------------------------------------
    # Create an admin user
    # NOTE: password_hash must be a real hashed password.
    # ---------------------------------------------
    op.execute("""
        INSERT INTO core.users (
            user_id, email, password_hash, display_name,
            is_active, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(),
            'admin@example.com',
            '$2b$12$abcdefghijklmnopqrstuv/hashedpasswordexample',
            'System Administrator',
            TRUE,
            NOW(),
            NOW()
        )
        ON CONFLICT (email) DO NOTHING;
    """)

    # ---------------------------------------------
    # Link admin user to default org
    # ---------------------------------------------
    op.execute("""
        INSERT INTO core.user_org_roles (
            user_org_role_id, org_id, user_id, role,
            is_primary, created_at
        )
        SELECT
            gen_random_uuid(),
            o.org_id,
            u.user_id,
            'admin',
            TRUE,
            NOW()
        FROM core.organizations o, core.users u
        WHERE u.email = 'admin@example.com'
        LIMIT 1;
    """)

    # ---------------------------------------------
    # Create a basic Chart of Accounts
    # ---------------------------------------------
    op.execute("""
        INSERT INTO acct.chart_of_accounts (
            account_id, org_id, code, name, type, is_active,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            o.org_id,
            '1000',
            'Cash',
            'asset',
            TRUE,
            NOW(),
            NOW()
        FROM core.organizations o
        ON CONFLICT (org_id, code) DO NOTHING;
    """)


def downgrade() -> None:
    """
    Remove baseline system data.
    """
    op.execute("DELETE FROM acct.chart_of_accounts WHERE code = '1000';")
    op.execute("DELETE FROM core.user_org_roles WHERE role = 'admin';")
    op.execute("DELETE FROM core.users WHERE email = 'admin@example.com';")
    op.execute("DELETE FROM core.organizations WHERE name = 'Default Organization';")
