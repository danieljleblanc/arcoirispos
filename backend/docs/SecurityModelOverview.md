## **1. Core Security Principles**

ArcoirisPOS is built on top of modern cloud-application security standards, with four non-negotiable principles driving every design decision:

### **1. Zero Trust Data Boundaries**

No request is trusted by default — every access must prove:

* **Who the user is** (JWT authentication)
* **Which organization they belong to** (X-Org-ID header)
* **What role they hold** (RBAC)
* **Whether their role allows the attempted action**

### **2. Deterministic Multi-Tenant Isolation**

Every piece of data belongs to exactly one organization.
Cross-org leakage is impossible because:

* All queries filter by `org_id`
* All writes inject `org_id` server-side (never trusting payload input)
* RBAC prevents access without proper membership

### **3. Immutable Access Control**

Authorization is not stored client-side — it is derived server-side from:

* Cryptographically signed JWT tokens
* Role assignments in the database
* OrgContext dependency injection

### **4. Defense-in-Depth**

Security layers stack:

* Encrypted secrets (.env)
* Docker-isolated services
* Parameterized SQL (no injection risk)
* Role verification
* Org verification
* Token verification
* Business rule validation

A compromise in any one layer cannot break the system.

---

## **2. Authentication Layer (JWT)**

ArcoirisPOS uses **stateless, signed JWT access tokens** plus **refresh tokens**.

### **Access Token**

* Short-lived
* Required for all protected routes
* Contains:

  ```
  user_id
  issued_at
  expiration
  ```

### **Refresh Token**

* Long-lived
* Stored securely client-side
* Used only to obtain new access tokens
* Invalidated server-side if compromised

### **Security Strength**

* Signed using HS256 / HS512 (configurable)
* Cannot be forged
* Cannot be tampered with
* Cannot reveal passwords or roles

JWT is industry-standard for POS, SaaS, and mobile systems requiring scalable authentication.

---

## **3. OrgContext Architecture (Option A+)**

ArcoirisPOS uses a **stable, predictable, secure multi-tenant model** based on explicit per-request org selection:

### **Required Request Header**

```
X-Org-ID: <uuid>
```

### **Security Guarantees**

1. **User must belong to the organization**
   Enforced by RBAC queries against `core.user_org_roles`.

2. **User must have adequate role**
   Based on three dependencies:

   * `require_any_staff`
   * `require_admin`
   * `require_owner`

3. **Server never trusts frontend `org_id`**
   All write operations:

   ```python
   data["org_id"] = org_id
   ```

4. **Consistent tenant walling**
   All reads and writes scoped by:

   ```python
   .where(Model.org_id == org_id)
   ```

This ensures data isolation equal to industry-standard SaaS platforms.

---

## **4. RBAC (Role-Based Access Control)**

Roles currently supported:

* **owner**
* **admin**
* **manager**
* **cashier**
* **support**
* **viewer**

### **Security Enforcement**

| Permission Type        | Enforced By         | Roles Allowed                           |
| ---------------------- | ------------------- | --------------------------------------- |
| Staff actions (POS)    | `require_any_staff` | owner, admin, manager, cashier, support |
| Administrative actions | `require_admin`     | owner, admin, manager                   |
| Owner-level actions    | `require_owner`     | owner                                   |

### **Security Guarantees**

* No user can access data from an organization they are not associated with.
* No user can escalate their role.
* No user can bypass org boundaries, even with valid JWT.

---

## **5. Database Security**

### **PostgreSQL-level**

* Dedicated Docker container
* Encrypted at rest (host-level encryption recommended)
* Separate DB user for application
* Strong password (in `.env`)

### **Application-level**

* SQLAlchemy parameterized queries → SQL injection impossible
* UUID primary keys → prevents sequential ID scraping
* Soft deletes for auditability
* Alembic-controlled schema → no drift

### **Multi-Tenant Enforcement**

Every table includes:

```
org_id UUID NOT NULL
```

Service layer automatically enforces:

```
WHERE org_id = <from header>
```

---

## **6. Password & Credential Security**

### **Hashing**

All passwords are stored using:

```
bcrypt (cost=12)
```

* One of the strongest password hashing algorithms available
* Resistant to brute-force attacks
* Salted automatically
* Never reversible

### **Login Security**

* Passwords never leave secure HTTPS transport
* Wrong-password responses always use constant timing
* User accounts can be disabled without deletion

---

## **7. API-Level Security**

### **CORS**

Configured to allow only approved origins.

### **Rate limiting**

Can be added at ingress (cloud load balancer) or via FastAPI middleware.

### **Input validation**

Handled by Pydantic v2:

* Prevents malformed data
* Blocks unsafe input
* Enforces types and constraints

### **Common attack blocks**

* **SQL injection** ← SQLAlchemy parameterization
* **Mass assignment** ← Controlled schema + service injection
* **Org skipping** ← OrgContext enforcement
* **Privilege escalation** ← RBAC checks
* **Token forgery** ← Cryptographic signing

---

## **8. Network & Deployment Security**

### **Docker Isolation**

* Backend, frontend, and DB are separate containers
* Network boundaries enforced per container
* Database not publicly exposed except designated port

### **Future production setup (recommended)**

* Nginx reverse proxy
* HTTPS termination at load balancer
* Fail2Ban or WAF
* Daily backup rotation
* Monitoring + audit logs

---

## **9. Development Security**

Even during development:

* `.env` is never committed
* Secrets stay local
* Local DB runs on non-standard credentials
* Migrations ensure reproducibility

---

## **10. Summary: Why This Architecture Is Secure**

| Layer                     | Security Mechanism       | Threats Eliminated                  |
| ------------------------- | ------------------------ | ----------------------------------- |
| JWT Auth                  | Signed access tokens     | Credential reuse, session hijacking |
| RBAC                      | Role-scoped access rules | Privilege escalation                |
| OrgContext                | Forced org boundary      | Cross-tenant data leakage           |
| Server-side org injection | Never trusts client      | Payload manipulation                |
| PostgreSQL + SQLAlchemy   | Param queries            | SQL injection                       |
| Bcrypt Hashing            | Non-reversible           | Password theft                      |
| Docker Isolation          | Container sandbox        | Host-level compromise               |
| Alembic Migrations        | Schema consistency       | Drift, injection via schema changes |

This layered system is secure enough for:

* Multi-tenant POS
* Payment systems
* Inventory and transactional records
* Small enterprise SaaS

It is *significantly more secure* than the architectures used by older legacy systems (QuickBooks, Aloha, NCR Silver, Square’s original builds, etc.).
