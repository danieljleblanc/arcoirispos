# backend/src/app/infrastructure/migrations/script.py.mako

"""baseline schema lock

Revision ID: 394e34d24016
Revises: <new_id>
Create Date: 2025-11-27 15:46:16.549862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '394e34d24016'
down_revision: Union[str, Sequence[str], None] = '<new_id>'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
