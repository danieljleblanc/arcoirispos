# Changelog

All notable changes to this project will be documented in this file.

This project follows **Semantic Versioning**.

---

## Table of Contents

- [0.13.0 — Customer Model Rewrite & Schema Realignment](#0130--customer-model-rewrite--schema-realignment)
- [0.12.0 — Unified Migration Baseline & Backend Stabilization](#0120--unified-migration-baseline--backend-stabilization)

---

## [0.13.0] — 2025-11-30  
### 👤 Customer Model Rewrite & Schema Realignment
<a id="0130--customer-model-rewrite--schema-realignment"></a>

This release introduces a complete rewrite of the Customer domain model, correcting architectural drift and aligning the POS customer subsystem with real-world business requirements. The update also includes a corrected seed file and schema fixes that fully stabilize customer creation, display, and future extensibility.

---

### 🧬 Customer Model Normalization

Replaced the old single-field `full_name` with a fully normalized structure:

- `first_name`  
- `middle_name`  
- `last_name`  
- `street_address`  
- `city`  
- `state`  
- `zip`  
- `phone`  
- `email`  
- `created_by`  
- `last_edited_by`  
- `last_edited_at`  
- `deleted_at` *(soft-delete lifecycle)*  

This modernization aligns the customer domain with CRM and retail data standards, enabling accurate reporting, filtering, and auditing.

---

### 🛠️ Seed File Corrections

- Updated `seed_dev_data.py` for the new Customer model.  
- Added a fully normalized default customer.  
- Updated default location, item, and terminal seeds for structural consistency.  
- Ensured schemas are created **before** metadata initialization.  

---

### 🧱 Schema & ORM Fixes

- Updated SQLAlchemy mappings for new fields.  
- Removed deprecated fields (`full_name`, `notes`, JSON address).  
- Synchronized Customer, Terminal, Location, and Item models with database structure.  
- Introduced a new baseline-compatible **Alembic-first workflow**.  

---

### 🔧 Backend Stability Improvements

- Verified required PostgreSQL extensions (`citext`, `pgcrypto`) load before metadata creation.  
- Removed seed failures referencing obsolete fields.  
- Ensured schema creation order: **core → acct → inv → pos**.  

---

### 🔖 Tag  
**v0.13.0-migration-customer-fix-2025-11-30**

---

## [0.12.0] — 2025-11-30  
### 🚀 Unified Migration Baseline & Backend Stabilization
<a id="0120--unified-migration-baseline--backend-stabilization"></a>

This release establishes a clean, authoritative migration baseline and stabilizes the entire backend development environment, resolving issues with Alembic migration drift, Docker filesystem divergence, and inconsistent schema states across machines.

---

### 🧩 Migration System Overhaul

- Removed all previous Alembic migration revisions.  
- Introduced a single authoritative baseline:  
  **`0001_initial_system_schema.py`**  
- Ensures correct creation of:
  - PostgreSQL extensions **citext**, **pgcrypto**  
  - Application schemas **core**, **acct**, **inv**, **pos**  
- Migration now uses Alembic-managed connections (`op.get_bind()`).  
- Eliminated duplicate/obsolete migration chains.  

---

### 🔧 Backend Environment Stabilization

- Restored correct backend volume mount: `./backend:/app`  
- Eliminated host/container filesystem divergence.  
- Ensured Alembic-generated migrations appear instantly on host.  
- Rebuilt environment to maintain consistent dev states.  

---

### 🗄️ Schema Initialization Verification

Successful fresh DB initialization now produces expected tables across:

- **core**  
- **acct**  
- **inv**  
- **pos**

Confirmed Alembic HEAD matches `0001`.

---

### 📝 Documentation

- Added updated migration guide.  
- Attached `backend.zip` to GitHub release.  
- Updated backend structure docs.  

---

### 🛠 Developer Notes

After pulling this version:

```bash
# Reset local Postgres volume
# Rebuild Docker
alembic upgrade head
Future migrations:

alembic revision --autogenerate -m "Describe your change"