"""
Initial system schema

Revision ID: 0001
Revises:
Create Date: 2025-11-27
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy import text
from src.app.core.base import Base

# Import all models so Base.metadata is populated
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

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Extensions
    bind.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
    bind.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    # Schemas
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS acct"))
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS inv"))
    bind.execute(text("CREATE SCHEMA IF NOT EXISTS pos"))

    # Tables
    Base.metadata.create_all(bind=bind)


def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)

    bind.execute(text("DROP SCHEMA IF EXISTS pos CASCADE"))
    bind.execute(text("DROP SCHEMA IF EXISTS inv CASCADE"))
    bind.execute(text("DROP SCHEMA IF EXISTS acct CASCADE"))
    bind.execute(text("DROP SCHEMA IF EXISTS core CASCADE"))

    bind.execute(text("DROP EXTENSION IF EXISTS pgcrypto CASCADE"))
    bind.execute(text("DROP EXTENSION IF EXISTS citext CASCADE"))
