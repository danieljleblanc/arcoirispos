
# 🧭 ArcoIrisPOS — Alembic Migration System Guide

This document explains the full migration architecture for the **ArcoIrisPOS Backend**, including the baseline collapse, the migration chain, how to rebuild the database, and how to safely create new migrations going forward.

---

# 🚀 1. Overview

The project uses **Alembic** for database schema migrations.

The migration system has been fully normalized into a clean, linear, dependable chain:

```

versions/
├── 000000000001_baseline_schema_collapse.py
├── 37a02ec8662a_init_schema.py
├── 853113448960_template_sanity_test.py
└── 2864583ca021_seed_initial_data.py

```

### Migration flow:

```

BASE
↓
000000000001   (baseline collapse)
↓
37a02ec8662a   (full schema)
↓
853113448960   (template sanity test)
↓
2864583ca021   (seed initial data)

```

This migration chain produces a complete, ready-to-use database.

---

# 📂 2. Directory Structure

```

src/database/migrations/
├── env.py
├── README_MIGRATIONS.md   <-- (this file)
└── versions/
├── 000000000001_baseline_schema_collapse.py
├── 37a02ec8662a_init_schema.py
├── 853113448960_template_sanity_test.py
└── 2864583ca021_seed_initial_data.py

```

The root project directory also contains the project-wide Alembic config file:

```

alembic.ini

````

---

# ⚙️ 3. How `env.py` Works

The custom `env.py` supports:

- Multi-schema migrations (`core`, `acct`, `inv`, `pos`)
- Autogenerate safety filters
- Prevention of empty migrations
- SQLAlchemy model loading (`src.models`)
- Server default comparison disabled (recommended)
- Fully correct handling of `alembic_version`

This ensures accurate and clean schema diffing for future revisions.

---

# 🧱 4. The Baseline Migration

**File:** `000000000001_baseline_schema_collapse.py`

This is the authoritative definition of the entire ArcoIrisPOS database.

It includes:

- Schema creation
- Postgres extensions
- Every table
- Every ENUM
- Every constraint
- Foreign keys
- Unique indexes
- Defaults
- JSONB fields
- Numeric precision
- Timestamps
- All business-layer relationships

This single file replaces all previous “init” or bootstrap scripts.

For a fresh install, all schema is created from this baseline.

---

# 🌱 5. Seed Data Migration

**File:** `2864583ca021_seed_initial_data.py`

This migration inserts:

- A default organization
- Initial admin user
- Core system linkage
- Any base chart-of-accounts items

This runs automatically after schema creation.

It is fully isolated from schema migrations.

---

# 🔧 6. Running Migrations

### Upgrade to the latest revision:

```bash
alembic upgrade head
````

### Apply a specific revision:

```bash
alembic upgrade 37a02ec8662a
```

### Downgrade to base:

```bash
alembic downgrade base
```

---

# 🔄 7. Full Reset (Development Only)

These commands wipe the database **completely**, including the Docker volume, and rebuild everything from scratch:

```bash
docker stop arcoirispos_postgres
docker rm arcoirispos_postgres
docker volume rm arcoirispos_postgres_data
docker-compose up -d postgres
alembic upgrade head
```

This ensures a clean test of your entire migration chain.

---

# 🧪 8. Creating New Migrations (Correct Method)

Use autogenerate:

```bash
alembic revision --autogenerate -m "describe change"
```

Your `env.py` ensures:

* Only meaningful changes are detected
* Empty migrations are removed
* All schemas are compared correctly

### Never modify older migration files.

Create a new revision **for every schema change**, even if tiny.

---

# 🔍 9. Schema Drift Checking

To detect whether ORM models differ from the live DB:

```bash
alembic revision --autogenerate -m "drift check" --rev-id drift_check
```

If identical, autogenerate will produce a revision that your hooks remove safely.

---

# ⚠️ 10. Downgrade Rules

### Downgrading to `base`:

* Drops all schemas
* Removes all tables, enums, and extensions
* Wipes **everything**

Safe only for dev use.

### Downgrading one step:

```bash
alembic downgrade -1
```

---

# 🛡️ 11. Migration Safety Rules (Important)

1. **Never edit existing migration files** after they land in Git.
2. Always create new revisions for all schema changes.
3. Autogenerate whenever possible.
4. Migration IDs must be unique.
5. Seed data stays isolated from schema.
6. Do not rename schemas (`acct`, `core`, `inv`, `pos`).
7. Validate your migration chain after each major change:

   ```bash
   alembic upgrade head
   ```

---

# 🧰 12. Troubleshooting

### **Error:** “relation X does not exist”

Cause: Wrong migration order or missing dependencies.
Fix: Verify `down_revision` chain in the `versions` directory.

---

### **Error:** Empty autogenerate script produced

Cause: No ORM schema differences
Fix: Normal — your schema matches perfectly.

---

### **Error:** Duplicate enum or type

Cause: Enum type exists in DB before migration
Fix: Baseline already handles `checkfirst=True` for ENUM creation.

---

### **Error:** Alembic version table in wrong schema

Fix: Ensure:

```python
version_table_schema=None
```

in `env.py`.

---

# 🎉 13. Summary

You now have:

✔ A clean baseline schema
✔ A stable migration chain
✔ Proper seeding
✔ Safe autogeneration
✔ A reproducible DB reset process
✔ A predictable future migration workflow

This file should be kept with the migration system and updated only when workflows change.
