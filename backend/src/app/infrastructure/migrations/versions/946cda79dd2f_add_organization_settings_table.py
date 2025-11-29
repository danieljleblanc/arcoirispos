"""Add organization_settings table

Revision ID: 946cda79dd2f
Revises: 35ee039b18b4
Create Date: 2025-11-29 02:14:55.478407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '946cda79dd2f'
down_revision: Union[str, Sequence[str], None] = '35ee039b18b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization_settings",
        sa.Column("org_settings_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", sa.UUID(), sa.ForeignKey("core.organizations.org_id", ondelete="CASCADE"), nullable=False),

        # POS rounding settings
        sa.Column("rounding_mode", sa.Text(), nullable=False, server_default=sa.text("'nearest_0.01'")),
        sa.Column("rounding_increment", sa.Numeric(10, 4), nullable=False, server_default=sa.text("0.01")),

        # Inventory reservation settings
        sa.Column("reserve_on_add", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("release_on_suspend", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),

        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),

        schema="core",
    )

    # One settings row per organization
    op.create_unique_constraint(
        "uq_organization_settings_org_id",
        "organization_settings",
        ["org_id"],
        schema="core"
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_organization_settings_org_id",
        "organization_settings",
        schema="core"
    )
    op.drop_table("organization_settings", schema="core")
