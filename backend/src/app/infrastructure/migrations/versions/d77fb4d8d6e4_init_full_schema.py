"""
Init full schema

Revision ID: d77fb4d8d6e4
Revises: 000000000002
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text
from src.app.core.base import Base

# Import all models so Base.metadata is fully populated
from src.app.org.models import (
    organization_models,
    role_models,
    user_models,
)

from src.app.accounting.models import (
    account_models,
    bank_account_models,
    customer_balance_models,
    journal_models,
    journal_line_models,
)

from src.app.inventory.models import (
    item_models,
    location_models,
    stock_level_models,
    stock_movement_models,
)

from src.app.pos.models import (
    customer_models,
    payment_models,
    sale_models,
    terminal_models,
    tax_rate_models,
)

revision: str = "d77fb4d8d6e4"
down_revision: Union[str, Sequence[str], None] = "000000000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Always use Alembic's connection (DO NOT create a new engine)
    bind = op.get_bind()

    # Ensure schemas exist (safe even if they already exist)
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS acct"))
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS inv"))
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS pos"))

    # Now create all tables using Alembic's same transactional connection
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
