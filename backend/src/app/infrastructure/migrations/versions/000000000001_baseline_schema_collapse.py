"""
Full schema baseline collapse

Revision ID: 000000000001
Revises:
Create Date: 2025-11-18
"""

from typing import Sequence, Union
from alembic import op

revision: str = "000000000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Only schemas + extensions belong in the baseline
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS acct")
    op.execute("CREATE SCHEMA IF NOT EXISTS inv")
    op.execute("CREATE SCHEMA IF NOT EXISTS pos")

    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS pos CASCADE")
    op.execute("DROP SCHEMA IF EXISTS inv CASCADE")
    op.execute("DROP SCHEMA IF EXISTS acct CASCADE")
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
