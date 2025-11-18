"""template sanity test

Revision ID: 853113448960
Revises: 37a02ec8662a
Create Date: 2025-11-18 14:01:23.080384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '853113448960'
down_revision: Union[str, Sequence[str], None] = '37a02ec8662a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
