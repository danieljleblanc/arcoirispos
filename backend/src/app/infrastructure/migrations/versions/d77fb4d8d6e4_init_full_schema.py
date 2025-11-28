# backend/src/app/infrastructure/migrations/script.py.mako

"""init full schema

Revision ID: d77fb4d8d6e4
Revises: 000000000002
Create Date: 2025-11-27 15:07:08.878955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd77fb4d8d6e4'
down_revision: Union[str, Sequence[str], None] = '000000000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
