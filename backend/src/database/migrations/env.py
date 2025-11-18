from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Import your models Base and settings
from src.models import Base
from src.core.config import settings

config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata
target_metadata = Base.metadata


# ---------------------------------------------------------
# ALEMBIC AUTOGENERATE FILTERS
# ---------------------------------------------------------

def include_object(object, name, type_, reflected, compare_to):
    # Ignore ONLY the core accidental version table (just in case)
    if type_ == "table" and getattr(object, "schema", None) == "core" and name == "alembic_version":
        return False

    # Accept everything else
    return True


def process_revision_directives(context, revision, directives):
    """
    Prevent autogenerate from creating empty migrations.
    """
    if not directives:
        return

    script = directives[0]
    if script.upgrade_ops.is_empty():
        directives[:] = []


# ---------------------------------------------------------
# MIGRATION MODES
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations without DB connection."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
        compare_type=True,
        compare_server_default=False,
        process_revision_directives=process_revision_directives,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema=None,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with live DB connection."""
    engine = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=False,
            include_object=include_object,
            include_schemas=True,
            version_table_schema=None,
            render_as_batch=True,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
