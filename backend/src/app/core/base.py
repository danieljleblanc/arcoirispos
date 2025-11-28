# src/app/core/base.py

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Global SQLAlchemy Base class for all ORM models."""
    pass
    
    # Import all ORM models so Alembic can autogenerate
from src.app.org import models as org_models          # noqa
from src.app.auth import models as auth_models        # noqa
from src.app.accounting import models as acct_models  # noqa
from src.app.inventory import models as inv_models    # noqa
from src.app.pos import models as pos_models          # noqa
