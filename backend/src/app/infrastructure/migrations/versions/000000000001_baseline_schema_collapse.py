"""
Full schema baseline collapse

Revision ID: 000000000001
Revises:
Create Date: 2025-11-18
"""

from typing import Sequence, Union
from alembic import op


# ============================================================
# Alembic identifiers
# ============================================================
revision: str = "000000000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


# ============================================================
# UPGRADE — baseline environment
# ============================================================
def upgrade() -> None:

    # --------------------------------------------------------
    # PostgreSQL extensions
    # --------------------------------------------------------
    # CITEXT — case-insensitive text
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    # PGCRYPTO — required for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # --------------------------------------------------------
    # Application schemas
    # --------------------------------------------------------
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS acct")
    op.execute("CREATE SCHEMA IF NOT EXISTS inv")
    op.execute("CREATE SCHEMA IF NOT EXISTS pos")


# ============================================================
# DOWNGRADE — remove everything
# ============================================================
def downgrade() -> None:

    # --------------------------------------------------------
    # Drop schemas first (CASCADE handles all dependent objects)
    # --------------------------------------------------------
    op.execute("DROP SCHEMA IF EXISTS pos CASCADE")
    op.execute("DROP SCHEMA IF EXISTS inv CASCADE")
    op.execute("DROP SCHEMA IF EXISTS acct CASCADE")
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")

    # --------------------------------------------------------
    # Drop extensions last
    # --------------------------------------------------------
    # (These must be dropped last because schemas/tables may depend on them)
    op.execute("DROP EXTENSION IF EXISTS pgcrypto CASCADE")
    op.execute("DROP EXTENSION IF EXISTS citext CASCADE")
