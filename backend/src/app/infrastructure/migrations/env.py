# backend/src/app/infrastructure/migrations/env.py

from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

from src.app.core.base import Base
from src.app.core.config import settings


# ---------------------------------------------------------
# CONFIG USED ONLY DURING ALEMBIC RUNTIME
# (Never executed at module import)
# ---------------------------------------------------------

def get_config_safe():
    """
    Safe wrapper so this file can be imported by validators/tests
    without triggering Alembic environment initialization.
    """
    try:
        return context.config
    except Exception:
        return None


# ---------------------------------------------------------
# FILTER RULES
# ---------------------------------------------------------

def include_object(obj, name, type_, reflected, compare_to):
    if (
        type_ == "table"
        and getattr(obj, "schema", None) in {"core", "acct", "inv", "pos"}
        and name == "alembic_version"
    ):
        return False
    return True


def process_revision_directives(context, revision, directives):
    if directives:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []


# ---------------------------------------------------------
# OFFLINE MODE
# ---------------------------------------------------------

def run_migrations_offline(cfg):
    url = cfg.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        include_schemas=True,
        compare_type=True,
        compare_server_default=False,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# ONLINE MODE
# ---------------------------------------------------------

def run_migrations_online(cfg):
    engine = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            include_schemas=True,
            compare_type=True,
            compare_server_default=False,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# ALEMBIC ENTRYPOINT
# (Only runs when Alembic invokes this script, NOT on import)
# ---------------------------------------------------------

def run_migrations():
    cfg = get_config_safe()

    # If imported by validator, abort safely.
    if cfg is None:
        # Do nothing — importing env.py is safe now.
        return

    if cfg.config_file_name:
        fileConfig(cfg.config_file_name)

    if context.is_offline_mode():
        run_migrations_offline(cfg)
    else:
        run_migrations_online(cfg)


# IMPORTANT:
# ❗ Do NOT call run_migrations() here.
# Alembic itself invokes it.
