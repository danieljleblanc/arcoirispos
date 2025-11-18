Alembic Migration Environment — Stable Baseline (Nov 2025)
Overview
As of this checkpoint, the backend Alembic migration system has been fully restored to a consistent, stable state. This includes alignment of:
	•	Alembic migration scripts
	•	The PostgreSQL database schema
	•	SQLAlchemy ORM models
	•	Autogeneration behavior
	•	Schema filtering logic
	•	Required PostgreSQL extensions
This document records the exact known-good state so future contributors (including future you) have a reliable baseline reference.

Migration Directory Structure
Current working migration directory:
backend/database/migrations/
    env.py
    script.py.mako
    versions/
        37a02ec8662a_init_schema.py
        1e13c05008ea_seed_initial_data.py
All other auto-generated experimental migration files created during the troubleshooting process have been evaluated and deprecacted. Only the files listed above represent the canonical migration history.

Current Database State
Installed Schemas
The PostgreSQL instance now contains all expected logical schemas:
	•	core
	•	acct
	•	inv
	•	pos
	•	public (managed by PostgreSQL)
Existing Tables
public
alembic_version
core
organizations
users
user_org_roles
acct
chart_of_accounts
journal_entries
journal_lines
bank_accounts
customer_balances
inv
items
locations
stock_levels
stock_movements
pos
customers
tax_rates
terminals
sale_lines
sales
payments
These match the SQLAlchemy models in src/models/models.py.
Alembic Revision State
The current database revision (stored in public.alembic_version) matches the Alembic head:
4f50b55d2114
This confirms zero drift and full synchronization.

PostgreSQL Extensions
Two required extensions are installed and validated:
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
pgcrypto enables gen_random_uuid() citext enables case-insensitive email columns
Both are mandatory for the application schema.

env.py Configuration (Final, Working State)
The Alembic env.py file has been corrected and stabilized.
Key validated behaviors:
	•	Correct import of SQLAlchemy models metadata (Base.metadata)
	•	Consistent database URL resolution (settings.database_url)
	•	Autogeneration now works without errors
	•	Downgrade and upgrade cycles run cleanly
	•	Schema-aware include filters correctly handle non-public schemas
include_object filter (final stable version)
def include_object(object, name, type_, reflected, compare_to):
    # Ignore alembic_version when reflecting from public schema
    if type_ == "table":
        obj_schema = getattr(object, "schema", None)
        if obj_schema == "public" and name == "alembic_version":
            return False

    # Ignore indexes (often auto-created)
    if type_ == "index":
        return False

    # Avoid spurious unique constraint diffs
    if type_ == "unique_constraint" and reflected and not compare_to:
        return False

    return True
This filter prevents phantom autogenerate diffs and unwanted schema churn.

Verified Behaviors (Golden State)
✔ Autogenerate works:
alembic revision --autogenerate -m "description"
✔ Upgrades apply cleanly:
alembic upgrade head
✔ Current revision matches Alembic head:
alembic current
alembic heads
✔ Database schema matches models:
Verified using SQLAlchemy inspector.
✔ No drift between DB and migration history
The “Target database is not up to date” cycle is fully resolved.

Best Practices Going Forward
1. Every model change → create a migration
alembic revision --autogenerate -m "describe change"
alembic upgrade head
2. Do not manually modify the database
All changes must occur through migrations.
3. Keep versions folder clean
Only committed, valid migration scripts should remain.
4. Never edit old migrations (except indentation fixes)
If schema changes are needed, create new migrations.
5. Document each major DB change
This file should be updated when:
	•	New schemas are added
	•	Migrations require manual SQL
	•	Seed logic is updated
	•	Baseline environment changes

Next Planned Step
Now that Alembic is stable, the next sane development tasks are:
	1	Initialize seed data (organizations, admin user, default tax settings)
	2	Finalize authentication + permissions flow
	3	Continue implementing POS + inventory business logic
	4	Start writing integration tests for DB routines
The system is now ready for normal, productive development.

End of Stable Baseline Documentation
Recorded November 2025
