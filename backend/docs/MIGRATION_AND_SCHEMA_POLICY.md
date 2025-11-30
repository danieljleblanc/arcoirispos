# backend/docs/MIGRATION_AND_SCHEMA_POLICY.md

# Migration & Schema Policy
ArcoirisPOS Backend  
_Last updated: 2025-11-30_

This document defines the rules, practices, and expectations for managing
database schema changes using Alembic. It prevents future drift, broken
upgrade paths, and multi-engine inconsistencies.

---

# 1. Baseline Migration (Required Reading)

The backend uses a **single authoritative migration**:

backend/src/app/infrastructure/migrations/versions/0001_initial_system_schema.py


This migration:

- Creates all PostgreSQL schemas (`core`, `acct`, `inv`, `pos`)
- Creates required extensions (`citext`, `pgcrypto`)
- Creates all tables from SQLAlchemy models
- Establishes the canonical Alembic version

**Never edit 0001 after release.**  
If you need to change core tables, always create a new migration.

---

# 2. Creating New Migrations

Always use:

```bash
alembic revision --autogenerate -m "Describe your change"

Requirements:

All models must be imported in env.py

Always run autogenerate inside the backend container

Ensure container uses bind mount (./backend:/app) so files appear locally

# 3. Applying Migrations

Always apply migrations using:

alembic upgrade head

You must apply migrations every time:

A new branch adds schema changes

A new version is tagged

After pulling latest main if migrations were added

# 4. Local Development Database Reset

To rebuild DB from scratch:

docker compose down
docker volume rm postgres_data
docker compose up -d
alembic upgrade head

# 5. Rules for Migration Safety
DO:

Use autogenerate for modifications

Review generated diff manually

Follow patterns from repositories

Tag releases whenever schema changes occur

DO NOT:

Modify old migrations (prevents reproducibility)

Create tables manually in SQL

Bypass Alembic

Use Python Enums as DB types

Mix runtime engine connections with Alembic connections

# 6. Schema Conventions

All tables belong to one of:

core

acct

inv

pos

Table names use snake_case

Foreign keys must reference full schema paths

UUIDs generated using gen_random_uuid()

# 7. Debugging Tools

Useful commands:

alembic current
alembic history
psql -U arcoiris_user -d arcoirispos_dev -c "\dn"
psql -U arcoiris_user -d arcoirispos_dev -c "\dt core.*"

# 8. Summary

This policy ensures:

Safe schema evolution

Reproducible builds

Clean upgrade paths

Consistent developer experience

Following these rules prevents the problems that motivated the
migration baseline reset on 2025-11-30.


---

# ----------------------------------------------------------------------------------------------------------------------
# 📄 3. **DEVELOPMENT_ENVIRONMENT_SETUP.md**
# ----------------------------------------------------------------------------------------------------------------------

**File:**  
`backend/docs/DEVELOPMENT_ENVIRONMENT_SETUP.md`

---

```markdown
# Development Environment Setup
ArcoirisPOS Backend  
_Last updated: 2025-11-30_

This document explains how to set up, run, and maintain the backend
development environment using Docker and Alembic.

---

# 1. Requirements

- macOS or Linux
- Docker Desktop
- Python 3.12 (optional, for local scripts)
- Git

---

# 2. Project Directory Structure (Backend)

backend/
src/app/
docs/
infrastructure/
docker-compose.yml (in project root)


---

# 3. Starting the Backend

From repository root:

```bash
docker compose up --build -d

This launches:

PostgreSQL (with health checks)

FastAPI backend

React frontend (optional)

# 4. Backend Container Access

To enter backend container:

docker exec -it arcoirispos_backend bash

# 5. Database Access

docker exec -it arcoirispos_postgres bash
psql -U arcoiris_user -d arcoirispos_dev

Useful inside psql:

\dn      # list schemas
\dt *.*  # list all tables
\dt core.*

# 6. Running Migrations

After changing models:

docker exec -it arcoirispos_backend bash
alembic revision --autogenerate -m "Describe your change"
alembic upgrade head

# 7. Resetting the Development Database

docker compose down
docker volume rm postgres_data
docker compose up -d
alembic upgrade head

This gives you a completely fresh schema using the migration baseline.

# 8. File Syncing (Critical)

Your backend container must mount the backend directory:

./backend:/app

This ensures:

Alembic migrations generated inside Docker appear locally.

Code edits on host appear instantly inside container.

This is defined in:

docker-compose.yml → fastapi → volumes section

# 9. Hot Reloading

FastAPI uses Uvicorn's reload mode:

uvicorn src.app.main:app --reload

Automatic reload works only when the container sees file changes —
which requires correct volume mounting.

# 10. Summary

This guide ensures every developer can:

Boot the environment

Run migrations

Reset the DB

Access the backend

Understand sync behavior

It reflects the current architecture and post-reset environment (2025-11-30).

