# Changelog
All notable changes to this project will be documented in this file.

The format follows [Semantic Versioning](https://semver.org/).

---

## [v0.10.0] — 2025-11-22
### Added
- Implemented **Architecture Option A** for stable multi-tenant org handling.
- Introduced centralized `OrgContext` resolver in `src/core/security/org_context.py`.
- Added new secure admin seed credentials using bcrypt.
- Added developer documentation for architecture freeze and roadmap.

### Changed
- Updated all active API route files to use the new dependency signature.
- Standardized org validation and user/org/role enforcement across the system.
- Improved Docker volume paths and Postgres healthcheck stability.
- Repaired seed data migration (`2864583ca021`) and corrected password hashing.
- Updated authentication logic for consistent bcrypt verification.

### Fixed
- Resolved `UndefinedTableError` caused by invalid baseline migrations.
- Fixed `401 Unauthorized` caused by mismatched bcrypt rounds.
- Repaired login behavior for both seed admin and dev admin flow.
- Eliminated legacy org_id parameters from route endpoints.

### Removed
- Deleted deprecated routes from `src/api/api_old/`.
- Removed inconsistent or obsolete role logic paths.

---
