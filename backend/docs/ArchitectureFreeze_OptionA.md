# Architecture Freeze — Option A
Date: 2025-11-22  
Status: **APPROVED & FROZEN**

This document formalizes the backend architectural direction for ArcoirisPOS as of version v0.10.0.

---

## 1. Overview
Option A establishes a **clean, testable, stateless, multi-tenant architecture** built on three pillars:

1. **X-Org-ID request header**
2. **OrgContext resolver**
3. **Centralized RBAC enforcement**

This is now the *mandatory* request model for all endpoints going forward.

---

## 2. OrgContext
Located at:
src/core/security/org_context.py

### Responsibilities:
- Validate `X-Org-ID` exists
- Load the organization record
- Attach org_id to route dependencies
- Prevent cross-tenant access

No future routes may accept `org_id` as a path or query parameter.

---

## 3. Dependency Standard

Every route now follows:

```python
session: AsyncSession = Depends(get_session)
org_ctx = Depends(get_current_org)
user = Depends(require_any_staff)
Admin-only routes use:

python
Copy code
user = Depends(require_admin)
This guarantees:

User is authenticated

User belongs to the org

User has adequate role

Organization exists and is active

## 4. RBAC Enforcement
RBAC lives in:

bash
Copy code
src/core/security/dependencies.py
Roles:

owner

admin

manager

cashier

support

viewer (restricted)

All roles are validated per-org, ensuring correct tenancy isolation.

## 5. Authentication
JWT-based

Bcrypt password hashing via passlib

Seed migration now uses a modern secure bcrypt hash

Password-hash mismatches during development have been fixed and stabilized.

## 6. Migrations & Seed Data
All required baseline rows are seeded:

Organization

Admin user

User/org/role mapping

Default sales tax

This ensures bootstrapping is reliable.

## 7. Future Constraints
From v0.10.0 onward:

No architecture changes without an ADR

No reintroducing org_id in request bodies

All new routes must use OrgContext

All org-sensitive queries must filter by org_id at the service layer

This is now the official backend contract.
