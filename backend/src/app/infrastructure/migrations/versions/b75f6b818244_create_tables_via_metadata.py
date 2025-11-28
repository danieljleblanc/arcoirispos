# backend/src/app/infrastructure/migrations/b75f6b818244_create_tables_via_metadata.py

"""create tables via metadata

Revision ID: <new_id>
Revises: d77fb4d8d6e4         # <-- replace with your actual current head
Create Date: 2025-11-27
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import engine_from_config, pool
from alembic import context
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from src.app.core.base import Base

# revision identifiers, used by Alembic.
revision: str = "<new_id>"
down_revision: Union[str, Sequence[str], None] = "d77fb4d8d6e4"   # CHANGE THIS
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # -------------------------------------------------
    # 1. Create accounting ENUMs FIRST
    # -------------------------------------------------
    enum_acct_entry_type = postgresql.ENUM(
        "debit",
        "credit",
        name="acct_entry_type_enum",
        schema="acct",
        create_type=False,
    )
    enum_acct_entry_type.create(bind, checkfirst=True)

    # -------------------------------------------------
    # 2. Now create all tables from ORM
    # -------------------------------------------------
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()

    # Drop tables first
    Base.metadata.drop_all(bind=bind)

    # Drop ENUM second
    enum_acct_entry_type = postgresql.ENUM(
        name="acct_entry_type_enum",
        schema="acct",
    )
    enum_acct_entry_type.drop(bind, checkfirst=True)

