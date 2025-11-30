"""
Rounding_apply_to migration (NO-OP — logic replaced by earlier migration)

Revision ID: 3d23faeb49c5
Revises: 946cda79dd2f
Create Date: 2025-11-29
"""

from typing import Sequence, Union

# Alembic identifiers
revision: str = "3d23faeb49c5"
down_revision: Union[str, Sequence[str], None] = "946cda79dd2f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NO-OP: This field is now created in 946cda79dd2f
    pass


def downgrade() -> None:
    # NO-OP
    pass
