# backend/docs/ARCHITECTURE_OVERVIEW.md

# Backend Architecture Overview
ArcoirisPOS — Backend System Architecture  
_Last updated: 2025-11-30_

This document provides a clear technical overview of the backend system, its
modules, conventions, and architectural design. It is the primary document
new developers should read to understand how the backend is structured.

---

# 1. High-Level Architecture

The backend follows a layered, modular architecture:

API (FastAPI Routers)
↓
Services (Business Logic)
↓
Repositories (DB access, CRUD, queries)
↓
SQLAlchemy Models
↓
PostgreSQL (core, acct, inv, pos schemas)


Key design goals:
- Modular domain separation
- Consistent code organization
- Clear boundary between business logic and data access
- Predictable service/repository patterns
- Multi-tenancy support via OrgContext
- Clean and stable database schema

---

# 2. Project Structure Summary

backend/src/app/
core/ # Base models, config, db session, repositories
org/ # Organization, users, roles, org-settings
accounting/ # Chart of accounts, journals, balances, bank accounts
inventory/ # Items, locations, stock levels, stock movements
pos/ # Sales, payments, customers, terminals
auth/ # JWT, hashing, permissions, login, RBAC
infrastructure/
migrations/ # Alembic migrations + schema baseline


---

# 3. Database Schema Overview

The application uses **four PostgreSQL schemas**:

- `core` → organizations, users, user_org_roles  
- `acct` → chart_of_accounts, journals, balances, bank accounts  
- `inv` → items, locations, stock levels, stock movements  
- `pos` → customers, sales, lines, terminals, payments, tax rates  

All are created automatically via the baseline migration.

---

# 4. Enum Strategy

**Old system:** Python Enums persisted to database  
**Removed:** Due to Alembic/autogenerate complexity and enum drift  
**New system:** All enumerations now use:

- **Python strings**
- **Database TEXT columns**
- **Validation via Pydantic or string constants**

Benefits:
- Zero Alembic migration conflicts
- Clear string values stored in DB
- Model-testing consistency

---

# 5. Multi-Tenancy Model (OrgContext)

The backend uses a lightweight header-based multi-tenancy model:

- Incoming requests include `X-Org-ID`
- `OrgContext` extracts org_id and injects it into:
  - DB queries
  - Service methods
  - Repository filters

This ensures all operations are org-scoped.

---

# 6. Request Flow

Client → FastAPI Router → Dependency Injection
→ OrgContext → Service → Repository → DB


Example:

POST /api/sales
↓ extract org_id
↓ require authenticated user
↓ call SaleService.create_sale()
↓ SaleRepository.insert()
↓ INSERT INTO pos.sales ...


---

# 7. Conventions

### Routers
Each module has its own routers under:

/api/<module>/


### Services
Pure business rules, validation, orchestration.

### Repositories
Single-responsibility DB-access classes.

### Models
Use SQLAlchemy declarative models with explicit schemas.

### Schemas (Pydantic)
- Input/output validation
- Decouple API from DB models

---

# 8. Baseline Migration Requirement

The backend depends on a **single clean Alembic baseline**:

0001_initial_system_schema.py


Never modify this file after its version has been released.

---

# 9. Summary

This architecture is designed for:
- Long-term maintainability  
- Multi-module scalability  
- Stable migrations  
- Predictable developer experience  

Start your exploration with:
- `src/app/core/base.py`
- `src/app/core/base_repository.py`
- `src/app/main.py`

