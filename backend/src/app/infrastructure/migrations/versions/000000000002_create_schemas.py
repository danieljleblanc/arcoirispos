"""
(NO-OP) Schemas are created in baseline migration 000000000001.
This revision is preserved for historical migration continuity.
"""

from typing import Sequence, Union

# Alembic identifiers
revision: str = "000000000002"
down_revision: Union[str, Sequence[str], None] = "000000000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NO-OP: Schemas were created in the baseline (000000000001)
    pass


def downgrade() -> None:
    # NO-OP: Baseline teardown handles schema removal
    pass
