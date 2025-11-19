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

# **ArcoirisPOS Database Migration Graph & Documentation**

This document provides a **complete overview** of the Alembic migration sequence for the ArcoirisPOS backend. It includes a visual graph of the migration chain, detailed descriptions of each revision, and rules for maintaining the migration integrity going forward.

---

## **📌 Purpose of This Document**

* Establish the *canonical* migration order
* Prevent out-of-sequence migrations
* Document how the baseline collapse works
* Help future developers understand which migrations create schemas, tables, test stubs, and seed data
* Provide a safe workflow for adding new migrations

---

# **📈 Migration Graph (ASCII / Markdown Visual)**

```text
                       ┌──────────────────────────────┐
                       │        BASELINE START         │
                       │      (no revision present)    │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                         ┌────────────────────────────┐
                         │ 000000000001                │
                         │ Full Schema Baseline        │
                         │ baseline_schema_collapse.py │
                         └───────────────┬────────────┘
                                         │
                                         ▼
                         ┌────────────────────────────┐
                         │ 37a02ec8662a                │
                         │ Init Schema                 │
                         │ init_schema.py              │
                         └───────────────┬────────────┘
                                         │
                                         ▼
                         ┌────────────────────────────┐
                         │ 853113448960               │
                         │ Template Sanity Test       │
                         │ template_sanity_test.py    │
                         └───────────────┬────────────┘
                                         │
                                         ▼
                         ┌────────────────────────────┐
                         │ 2864583ca021               │
                         │ Seed Initial Data          │
                         │ seed_initial_data.py       │
                         └────────────────────────────┘
```

---

# **📄 Migration Revision Index**

| Order | Revision ID    | File Name                     | Description                                                            |
| ----: | -------------- | ----------------------------- | ---------------------------------------------------------------------- |
|     0 | *BASE*         | *no file*                     | Empty state before first migration                                     |
|     1 | `000000000001` | `baseline_schema_collapse.py` | Creates schemas & extensions only. This is the new canonical baseline. |
|     2 | `37a02ec8662a` | `init_schema.py`              | Full table & enum creation (core, acct, inv, pos).                     |
|     3 | `853113448960` | `template_sanity_test.py`     | No-op template migration (kept for history).                           |
|     4 | `2864583ca021` | `seed_initial_data.py`        | Inserts initial org/user/role/etc.                                     |

---

# **📌 Baseline Migration Behavior**

### The file `000000000001_baseline_schema_collapse.py`:

* **MUST remain minimal**
  ✔ Creates schemas
  ✔ Creates required extensions (`citext`, `pgcrypto`)
  ✘ **No tables**
  ✘ **No enums**
  ✘ **No foreign keys**
  ✘ **No sequences or seed data**

This ensures Alembic can:

* downgrade safely to baseline
* rebase future schemas
* allow clean rebuilds without reinitializing table content

---

# **🚀 Commands to Work With the Migration Graph**

### **Upgrade to latest**

```bash
alembic upgrade head
```

### **Downgrade to baseline**

```bash
alembic downgrade 000000000001
```

### **Downgrade ALL the way (dangerous)**

```bash
alembic downgrade base
```

### **Show the migration tree**

```bash
alembic history --verbose
```

---

# **📐 Rules for Future Migrations**

To keep the system stable:

### ✔ DO:

* Create new migrations using:

  ```bash
  alembic revision -m "description"
  ```
* Keep baseline **untouched forever**
* Place all schema changes in migrations **after** `37a02ec8662a`
* Ensure each migration:

  * is reversible
  * does not duplicate prior schema objects
  * maintains referential integrity

### ✘ DO NOT:

* Modify old migration files
* Add tables or types to the baseline
* Change revision IDs
* Change down_revision links retroactively
* Manually alter database schema outside Alembic

---

# **⚠️ Developer Warnings (Critical)**

### **1. Never rebuild the baseline again.**

This is a one-time operation.
The new canonical base is now `000000000001`.

### **2. Do not reorder migration history.**

Alembic depends on a strict DAG.

### **3. All future schema work MUST start after `37a02ec8662a`.**

### **4. If autogenerate ever outputs an empty migration:**

It should be automatically discarded (your env.py handles this).

### **5. If a migration fails during CI or local build:**

Run:

```bash
docker-compose down -v
docker-compose up -d
alembic upgrade head
```



