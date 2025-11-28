"""Create application schemas"""

from alembic import op

revision = "000000000002"
down_revision = "000000000001"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS acct")
    op.execute("CREATE SCHEMA IF NOT EXISTS inv")
    op.execute("CREATE SCHEMA IF NOT EXISTS pos")

def downgrade():
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
    op.execute("DROP SCHEMA IF EXISTS acct CASCADE")
    op.execute("DROP SCHEMA IF EXISTS inv CASCADE")
    op.execute("DROP SCHEMA IF EXISTS pos CASCADE")
