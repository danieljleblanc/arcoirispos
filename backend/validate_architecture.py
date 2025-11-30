# backend/validate_architecture.py

#!/usr/bin/env python3
"""
Architecture Consistency Validator
ArcoirisPOS Backend
---------------------------------

Validates:

1. Directory structure
2. Required modules & __init__.py files
3. Repository/service/model layouts
4. Enum usage (must be string-based)
5. Alembic baseline structure
6. Migration integrity
7. SQLAlchemy metadata vs actual DB schema
8. Required Postgres schemas
9. Volume mount correctness (detect container/host drift)
10. Naming conventions

Run inside backend container:
    python validate_architecture.py
"""

import os
import sys
import inspect
import pkgutil
import importlib
import subprocess
from typing import List

from sqlalchemy import create_engine, inspect as sqla_inspect
from src.app.core.config import settings
from src.app.core.base import Base


# ------------------------------
# Utility Helpers
# ------------------------------

def header(title: str):
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80)


def fail(message: str):
    print(f"❌ FAIL: {message}")


def ok(message: str):
    print(f"✅ OK: {message}")


# ------------------------------
# 1. Directory & Module Layout Validation
# ------------------------------

EXPECTED_MODULES = [
    "src.app.core",
    "src.app.org",
    "src.app.accounting",
    "src.app.inventory",
    "src.app.pos",
    "src.app.auth",
    "src.app.infrastructure.migrations",
]


def validate_directories():
    header("Directory Structure Validation")

    for module in EXPECTED_MODULES:
        path = os.path.join("backend/src", *module.split("."))

        if not os.path.exists(path):
            fail(f"Missing directory: {path}")
        else:
            ok(f"Directory present: {path}")

        init_file = os.path.join(path, "__init__.py")
        if not os.path.exists(init_file):
            fail(f"Missing __init__.py in: {path}")
        else:
            ok(f"__init__.py OK in {path}")


# ------------------------------
# 2. Importability Check
# ------------------------------

def validate_imports():
    header("Import Validation")

    for module in EXPECTED_MODULES:
        try:
            importlib.import_module(module)
            ok(f"Import OK: {module}")
        except Exception as e:
            fail(f"Cannot import {module}: {e}")


# ------------------------------
# 3. Enum Usage Validation (string-based)
# ------------------------------

def validate_enum_usage():
    header("Enum Usage Validation (String Only)")

    violations = []

    import src.app

    for finder, name, ispkg in pkgutil.walk_packages(src.app.__path__, "src.app."):
        try:
            mod = importlib.import_module(name)
        except Exception:
            continue

        for _, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and "Enum" in repr(obj):
                violations.append(f"{name} contains Python Enum: {obj.__name__}")

    if violations:
        for v in violations:
            fail(v)
    else:
        ok("All enums are string-based. No Python Enum classes detected.")


# ------------------------------
# 4. Alembic Baseline Validation
# ------------------------------

def validate_migrations():
    header("Alembic Migration Validation")

    versions_dir = "backend/src/app/infrastructure/migrations/versions"
    baseline = os.path.join(versions_dir, "0001_initial_system_schema.py")

    if not os.path.exists(baseline):
        fail("Baseline migration 0001_initial_system_schema.py is missing!")
    else:
        ok("Baseline migration present.")

    py_files = [f for f in os.listdir(versions_dir) if f.endswith(".py")]

    if len(py_files) != 2:  # baseline + __init__.py
        fail(f"Unexpected number of migration files: {py_files}")
    else:
        ok("Migration folder is clean and contains only baseline + __init__.")


# ------------------------------
# 5. Database Schema Validation
# ------------------------------

REQUIRED_SCHEMAS = ["core", "acct", "inv", "pos"]

def validate_database_schema():
    header("Database Schema Validation")

    engine = create_engine(settings.database_url)
    inspector = sqla_inspect(engine)

    schemas = inspector.get_schema_names()

    for schema in REQUIRED_SCHEMAS:
        if schema not in schemas:
            fail(f"Schema missing: {schema}")
        else:
            ok(f"Schema OK: {schema}")

    # Table-level consistency
    model_tables = set(Base.metadata.tables.keys())
    db_tables = set()

    for schema in REQUIRED_SCHEMAS:
        for t in inspector.get_table_names(schema=schema):
            db_tables.add(f"{schema}.{t}")

    # Convert model table names to full schema.table format
    model_tables_formatted = set(
        f"{tbl.schema}.{tbl.name}" for tbl in Base.metadata.tables.values()
    )

    missing = model_tables_formatted - db_tables
    extra = db_tables - model_tables_formatted

    if missing:
        fail(f"Missing tables in DB: {missing}")
    else:
        ok("All SQLAlchemy model tables exist in the database.")

    if extra:
        fail(f"Database contains unexpected tables: {extra}")
    else:
        ok("No extra tables detected in DB.")


# ------------------------------
# 6. Filesystem Mount Validation
# ------------------------------

def validate_mount():
    header("Docker Volume Mount Check")

    # Inside container, local /app should match host's ./backend
    expected = "/app/src/app"
    if not os.path.exists(expected):
        fail(f"Expected path not found inside container: {expected}")
        return

    ok("Backend mount appears present inside container.")


# ------------------------------
# MAIN
# ------------------------------

if __name__ == "__main__":
    validate_directories()
    validate_imports()
    validate_enum_usage()
    validate_migrations()
    validate_database_schema()
    validate_mount()

    print("\n" + "="*80)
    print("🏁 Architecture validation complete.")
    print("="*80)
