# backend/src/app/infrastructure/migrations/script.py.mako

"""baseline schema lock

Revision ID: 35ee039b18b4
Revises: 394e34d24016
Create Date: 2025-11-27 15:47:05.056636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '35ee039b18b4'
down_revision: Union[str, Sequence[str], None] = '394e34d24016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
