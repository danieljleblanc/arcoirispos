# 🔒 Security Policy  
ArcoírisPOS — Foreside Holdings LLC  
Proprietary Software • Private Repository

This document outlines the security practices and responsible disclosure
guidelines for the ArcoírisPOS system and associated repositories owned by
**Foreside Holdings LLC**.

Although this repository is currently private, these policies apply to all
internal contributors, contractors, and future public releases.

---

# 📌 Supported Versions

Only the active development branch(es) are supported:

| Version | Status        |
|--------|----------------|
| main   | Actively maintained |
| dev    | Actively maintained |

Older or archived branches are **not** maintained and may contain unresolved
security vulnerabilities.

---

# 🛡 Reporting a Security Issue

If you discover a security vulnerability, whether in the backend, frontend,
database schema, Docker environment, dependencies, or documentation:

### **Do NOT create a GitHub issue.**
### **Do NOT disclose it publicly.**

Instead, report it privately to:

**security@foresideholdings.com**  
(If this email becomes active later, update it here.)

If unavailable, report directly to:

**Daniel Joseph LeBlanc (Owner & Architect)**  
danieljleblanc@foresideholdings.com

Please include:

- A clear description of the vulnerability  
- Steps to reproduce  
- Severity level (if known)  
- Suggested remediation (optional)  
- Whether the vulnerability has been exploited (if known)

We will acknowledge receipt within **72 hours** and provide updates until resolved.

---

# 🔐 Internal Security Practices

All contributors must follow these internal security expectations:

### 1. **Secrets & Credentials**
- Never commit `.env` files, database passwords, API keys, or private certificates  
- All secrets must be stored in secure `.env` files ignored via `.gitignore`  
- Use encrypted storage or a secrets manager for long-term credentials  

### 2. **Dependencies**
- Backend dependencies (Python / FastAPI) must be kept updated  
- Frontend dependencies (NPM) must be regularly reviewed  
- Docker base images must be scanned for vulnerabilities  

Recommended tools:
- `pip-audit`  
- `npm audit`  
- Docker Hub security scans  
- OSV scanner  

### 3. **Access Control**
- Repository access should be limited to essential personnel  
- MFA must be enabled on all GitHub accounts with access  
- SSH keys must use strong cryptography  

### 4. **Database Security**
- Use least-privilege access for development databases  
- Use strong PostgreSQL passwords for local and production environments  
- Avoid exposing ports unnecessarily (especially PostgreSQL 5432)  

### 5. **Code Security**
- Use parameterized SQL (never string concatenation)  
- Validate and sanitize all user input  
- Avoid storing sensitive data in logs  

---

# 🚨 Handling Security Fixes

If a vulnerability is found and confirmed:

1. A security branch will be created (`security/fix-description`)  
2. A patch will be developed and tested internally  
3. Changes will be merged into `main` and `dev`  
4. A private advisory will be created for internal tracking  
5. If the repo becomes public later, a public advisory may be published  

---

# 🔒 Disclosure Policy

We request **90 days** for responsible disclosure before any public discussion.

Early disclosure without authorization is prohibited for both internal and external parties due to the proprietary nature of the system.

---

# 📄 Security Contact

**Foreside Holdings LLC**  
Security & Compliance  
Email: security@foresideholdings.com  
Alternate: danieljleblanc@foresideholdings.com

