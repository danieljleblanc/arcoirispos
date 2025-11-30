"""Add organization_settings table (NO-OP after full-schema init)

Revision ID: 946cda79dd2f
Revises: d77fb4d8d6e4
Create Date: 2025-11-29 00:00:00
"""

from typing import Sequence, Union

# Alembic identifiers
revision: str = "946cda79dd2f"
down_revision: Union[str, Sequence[str], None] = "d77fb4d8d6e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    NO-OP:
    The organization_settings table is already created by the
    full-schema initialization (d77fb4d8d6e4) via SQLAlchemy models.
    """
    pass


def downgrade() -> None:
    """
    NO-OP:
    This revision does not change schema state and therefore has
    nothing to undo independently.
    """
    pass
