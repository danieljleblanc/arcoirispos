# 🗄️ ArcoírisPOS — Schema Migration Guide  
Foreside Holdings LLC  
PostgreSQL • FastAPI • Domain-Driven SQL Migrations

---

# 📘 Overview

This guide documents the **database migration workflow** for ArcoírisPOS.  
It explains:

- How migrations are organized  
- How to create new migration files  
- How to apply migrations  
- Versioning and naming conventions  
- Best practices  
- Rollback procedures  
- Developer workflow integration  

ArcoírisPOS uses **pure SQL migrations** for full visibility, reliability, and transparent version control.

---

# 📁 Migration Directory Structure

All SQL migrations live under:

```
backend/
  database/
    migrations/
      001_init_arcoirispos.sql
      002_indexes.sql
      003_add_items_table.sql
      ...
    seeds/
      demo_data.sql
```

### Key Principles

- **Every schema change must have a migration file**
- **Migrations are immutable** once pushed to `main`
- **One migration = one logical change**
- **Migrations run in numeric order**

---

# 🔢 Migration Numbering

Migrations use **three-digit incremental numbering**:

```
001_
002_
003_
...
```

Each file name begins with:

```
###_meaningful_description.sql
```

Examples:

```
004_add_stock_movements.sql
005_add_acct_journal_tables.sql
006_alter_items_add_cost.sql
```

### ✔ Good descriptions:

- `add_users_table`
- `add_foreign_keys_pos_domain`
- `alter_items_add_cost_column`

### ❌ Bad descriptions:

- `new.sql`
- `fix.sql`
- `test123.sql`

---

# 🏗 Creating a New Migration

Whenever you modify *any* of the following:

- tables  
- columns  
- indexes  
- constraints  
- relationships  
- enums  
- seed data (production-relevant)  

You **must** create a migration.

---

# ✏️ Step-by-Step: Create a Migration

### 1. Determine migration number  
Look at the highest number in `migrations/`, then add 1.

Example:

Current files:

```
001_init_arcoirispos.sql
002_indexes.sql
003_add_inventory.sql
```

Your new file:

```
004_add_cost_to_items.sql
```

---

### 2. Create the SQL file

Example: `004_add_cost_to_items.sql`

```sql
-- Add cost column to items
ALTER TABLE items
ADD COLUMN cost numeric;
```

If your migration alters existing data, include an update:

```sql
UPDATE items SET cost = 0 WHERE cost IS NULL;
```

---

### 3. Save file under:

```
backend/database/migrations/
```

---

### 4. Apply migration to your local DB

```bash
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/004_add_cost_to_items.sql
```

---

### 5. Verify changes

Inside `psql`:

```sql
\d items;
```

Or test via API.

---

### 6. Commit the migration

```bash
git add backend/database/migrations/004_add_cost_to_items.sql
git commit -m "Add cost column to items table"
git push origin feature/my-branch
```

Then submit a Pull Request.

---

# ▶️ Applying All Migrations

To recreate a fresh database:

### 1. Drop the old DB (dev only)

```sql
DROP DATABASE arcoirispos_dev;
CREATE DATABASE arcoirispos_dev;
```

### 2. Apply migrations in numeric order

```bash
for f in backend/database/migrations/*.sql; do
  psql -U arcoiris_user -d arcoirispos_dev -f "$f"
done
```

Or manually run:

```bash
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/001_init_arcoirispos.sql
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/002_indexes.sql
...
```

---

# 🔄 Rollback / Undo Approach

ArcoírisPOS follows **forward-only migrations**, which is industry-standard.

Rollback is done by adding a *new migration* that reverses the change.

Example:

### Migration 004 (incorrect):

```sql
ALTER TABLE items
ADD COLUMN cost numeric;
```

### Rollback migration 005:

```sql
ALTER TABLE items
DROP COLUMN cost;
```

Never modify old migrations after merging into `main`.

---

# 🧪 Adding Seed Data

All development-only seed data should go into:

```
backend/database/seeds/demo_data.sql
```

### Seeding example:

```bash
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/seeds/demo_data.sql
```

Seed data includes:

- demo customers  
- demo items  
- demo inventory levels  

---

# 🧩 Domain-Specific Migration Guidance

Each domain follows the same principles.

---

## **core migrations**

Examples:

- add users  
- modify organizations  
- add roles or permissions  

Maintain strict FK relationships.

---

## **pos migrations**

Typical changes:

- add sale tables  
- change payment fields  
- add tax rules  
- enforce constraint on sale status  

Ensure totals remain numeric(12,2) or numeric without scale.

---

## **inv migrations**

Typical changes:

- add items  
- add locations  
- expand stock tracking  
- adjust movement table  
- enforce quantity constraints  

Most sensitive domain due to transactional volume.

---

## **acct migrations**

Accounting migrations must maintain **ledger integrity**:

- chart_of_accounts changes  
- new journal table fields  
- add RLS later  
- no breaking double-entry rules  

---

# 🧱 Constraints & Indexes

### Example PK:

```sql
ALTER TABLE items
ADD PRIMARY KEY (id);
```

### Example FK:

```sql
ALTER TABLE sales
ADD CONSTRAINT fk_sales_customers
FOREIGN KEY (customer_id) REFERENCES customers(id);
```

### Example index:

```sql
CREATE INDEX idx_items_sku ON items(sku);
```

Indexes **must** be in their own migration file if large.

---

# 🧬 Column Types

Recommended types:

| Purpose | Type |
|--------|------|
| IDs | UUID |
| Timestamps | TIMESTAMP WITH TIME ZONE |
| Currency | numeric(12,2) or numeric |
| Quantities | numeric |
| Flags | boolean |

---

# 🛡 Rules for Safe Migrations

- Never drop columns without confirming usage  
- Never modify past migrations  
- Always test migrations locally  
- Always increment migration numbers  
- All migrations must be deterministic  
- Every migration must be idempotent when possible  
- Avoid destructive operations in production environments  

---

# ❗ Dangerous Operations (Avoid in Production)

- `ALTER TABLE ... DROP COLUMN`  
- `UPDATE ...` without WHERE clause  
- Rebuilding large tables inside peak load windows  
- Making columns nullable/non-nullable without verifying data  

---

# 🧭 Developer Workflow Summary

### When making schema changes:

1. Create a new migration  
2. Apply locally  
3. Test API behavior  
4. Update `DATA_MODEL.md` if needed  
5. Commit migration file  
6. Submit PR  

Database integrity is critical — always treat migrations as permanent, irreversible system events.

---

# 🏁 Summary

This migration guide ensures:

- consistent schema evolution  
- traceable SQL changes  
- safe production handling  
- domain-driven database discipline  
- clean onboarding for new developers  

Every structural change to the ArcoírisPOS database **must** follow this guide.

