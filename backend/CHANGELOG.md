# Changelog
All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

---

## [0.10.1] — 2025-11-22
### Added
- Introduced unified **OrgContext (Option A+) architecture** using X-Org-ID header.
- Implemented the new `src/core/security/org_context.py` module.
- Added centralized RBAC dependencies using `require_any_staff` and `require_admin`.

### Changed
- Refactored all API route files to use the new org context signature.
- Updated authentication pipeline to align with new RBAC and org_id flow.
- Normalized database access patterns across POS and Inventory modules.
- Rebuilt Alembic seed migration with corrected bcrypt hashes.
- Updated security configuration and internal dependency wiring.

### Fixed
- Login failures due to incompatible bcrypt hashes.
- Swagger authentication flow (Bearer token now loads correctly).
- Route-level permission inconsistencies across POS/INV endpoints.
- Removed old legacy route prototypes under `src/api/api_old`.

### Removed
- Deleted all deprecated route definitions under `src/api/api_old/`.

---

## [0.10.0] — 2025-11-18
### Added
- Initial multi-org scaffolding.
- RBAC foundation (Role enum, UserOrgRole).
- First pass of security dependencies.
- POS + Inventory module routing structure.

---

## [0.9.0] — 2025-11-10
### Added
- Stable POS core (sales, items, customers, terminals).
- Stable Inventory core (locations, stock levels, movements).
- JWT authentication and refresh pipeline.
- Full Docker-based development environment.

---

## [0.8.0] — 2025-11-01
*Historic foundational commits.*

---

