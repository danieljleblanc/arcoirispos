# backend/src/app/infrastructure/migrations/script.py.mako

"""Add rounding_apply_to to organization_settings

Revision ID: 3d23faeb49c5
Revises: 946cda79dd2f
Create Date: 2025-11-29 02:42:41.578860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3d23faeb49c5'
down_revision: Union[str, Sequence[str], None] = '946cda79dd2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organization_settings",
        sa.Column(
            "rounding_apply_to",
            sa.Enum("none", "cash_only", "all_payments",
                    name="rounding_targets"),
            nullable=False,
            server_default='cash_only'
        ),
        schema="core",
    )


def downgrade() -> None:
    op.drop_column(
        "organization_settings",
        "rounding_apply_to",
        schema="core"
    )
    op.execute("DROP TYPE IF EXISTS rounding_targets;")
