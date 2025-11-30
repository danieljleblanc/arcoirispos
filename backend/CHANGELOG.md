# Changelog
All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

---

## [0.12.0] — 2025-11-30
### 🚀 Unified Migration Baseline & Backend Stabilization

This release establishes a clean, authoritative migration baseline and stabilizes
the entire backend development environment, resolving issues with Alembic
migration drift, Docker filesystem divergence, and inconsistent schema state
between environments.

#### 🧩 Migration System Overhaul
- Removed all previous Alembic migration revisions.
- Introduced a single authoritative baseline:
  - `0001_initial_system_schema.py`
- Ensures correct creation of:
  - PostgreSQL extensions `citext` and `pgcrypto`
  - Application schemas `core`, `acct`, `inv`, `pos`
- Uses Alembic-managed connections reliably (`op.get_bind()`).
- Eliminated previously duplicated and conflicting migration chains.

#### 🔧 Backend Environment Stabilization
- Restored correct volume mount for backend service (`./backend:/app`).
- Eliminated container/host filesystem divergence.
- Ensures Alembic-generated migrations appear instantly on the host filesystem.
- Rebuilt development environment for consistency across rebuilds.

#### 🗄️ Schema Initialization Verification
- Verified fresh DB initialization produces all expected tables across:
  - **core**, **acct**, **inv**, **pos**
- Confirmed Alembic HEAD aligns with `0001` after reset.

#### 📝 Documentation
- Added updated migration README files.
- Attached `backend.zip` snapshot to the GitHub release.
- Updated backend project structure documentation.

#### Developer Notes
After pulling this version:
- Reset your local Postgres volume.
- Rebuild Docker.
- Apply migrations with `alembic upgrade head`.
- Future migrations should now safely use:
  ```bash
  alembic revision --autogenerate -m "Describe your change"
