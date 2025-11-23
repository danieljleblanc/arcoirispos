# # **ArcoirisPOS Developer Onboarding Guide**

### *Backend Engineering — FastAPI / PostgreSQL / Docker*

---

## ## **1. Overview**

Welcome to the ArcoirisPOS backend development environment.
This guide ensures every developer can:

* run the backend locally
* understand the project structure
* know how migrations, security, and routes work
* contribute safely using our stable architecture (OrgContext / Option A+)
* follow our Git + Docker workflows

This guide assumes basic familiarity with Python, FastAPI, Docker, and PostgreSQL.

---

# # **2. System Requirements**

### **Required Tools**

| Tool                 | Version | Notes                             |
| -------------------- | ------- | --------------------------------- |
| Python               | 3.12.x  | Installed inside Docker container |
| Docker Desktop       | latest  | Required                          |
| Git                  | latest  | Required                          |
| VS Code or JetBrains | —       | Recommended                       |
| Make (optional)      | —       | Some developers prefer it         |

---

## ## **3. Repository Structure**

```
arcoirispos/
│
├── backend/
│   ├── src/
│   │   ├── api/                 ← All route controllers (FastAPI endpoints)
│   │   ├── core/
│   │   │   ├── security/        ← JWT, RBAC, OrgContext, password hashing
│   │   │   ├── database.py      ← async engine + session
│   │   ├── models/              ← SQLAlchemy ORM models (core, pos, inventory)
│   │   ├── services/            ← Business logic layer (POS + Inventory)
│   │   ├── main.py              ← FastAPI app
│   │   ├── wait_for_db.py       ← startup gatekeeper
│   │
│   ├── database/
│   │   ├── migrations/          ← Alembic migrations
│   │   ├── alembic.ini
│   │
│   ├── Dockerfile               ← FastAPI build
│   ├── .env                     ← environment secrets (dev only)
│
├── frontend/
│   └── arcoiris-frontend/       ← React POS UI
│
├── docker-compose.yml           ← Multi-service runtime
└── README.md
```

---

# # **4. Running the System**

### **Start the containers**

```
docker compose up --build
```

Services:

* FastAPI backend: [http://localhost:8000](http://localhost:8000)
* React frontend: [http://localhost:3000](http://localhost:3000)
* PostgreSQL database: localhost:5432
* Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### **Stop everything**

```
docker compose down
```

### **Reset database completely**

```
docker compose down -v
docker compose up --build
```

---

# # **5. Database: Alembic Migrations**

### **Enter backend container:**

```
docker exec -it arcoirispos_backend bash
```

### **Run migrations:**

```
alembic upgrade head
```

### **Generate a new migration:**

```
alembic revision -m "describe change"
```

### **Apply it:**

```
alembic upgrade head
```

---

# # **6. Authentication Architecture (Frozen)**

### **This is our final, stable architecture for v1.0.**

1. **JWT Authentication**

   * Login returns access + refresh tokens
   * Access token is required for all protected routes

2. **RBAC (Role-Based Access Control)**

   * Roles: owner, admin, manager, cashier, support, viewer
   * Enforced through:

```
require_any_staff
require_admin
```

3. **Organization Resolution — Option A+**

   * Every request must include:
     `X-Org-ID: <uuid>`

   * Resolved by dependency:
     `org_id = Depends(get_current_org)`

4. **Multi-tenant Safety**

   * All server-side writes **inject org_id**
   * No trust of frontend org_id
   * Cross-org access is automatically blocked

This design keeps things simple, clean, and secure — avoiding the complexity of option B or C until we are ready.

---

# # **7. How Routes Work**

Every protected route looks like this:

```python
@router.get("/")
async def list_something(
    session: AsyncSession = Depends(get_session),
    org_id = Depends(get_current_org),
    user = Depends(require_any_staff),
):
    return await service.get_by_org(session, org_id)
```

### **All routes follow the same pattern:**

| Responsibility | Source                            |
| -------------- | --------------------------------- |
| Auth (JWT)     | Authorization: Bearer             |
| Org            | X-Org-ID header                   |
| Role check     | require_any_staff / require_admin |
| Business logic | Service layer                     |
| Data access    | SQLAlchemy ORM                    |

This keeps files short and extremely consistent.

---

# # **8. Making Code Changes (Safe Workflow)**

### **1. Modify the model(s)**

Under `src/models/...`

### **2. Generate and edit Alembic migration**

```
docker exec -it arcoirispos_backend bash
alembic revision -m "add new field to items"
```

Migration goes into:

```
backend/src/database/migrations/versions/
```

### **3. Update service layer logic**

Under: `src/services/...`

### **4. Update route(s)**

Under: `src/api/...`

### **5. Rebuild and test**

```
docker compose down -v
docker compose up --build
```

### **6. Run Swagger tests**

[http://localhost:8000/docs](http://localhost:8000/docs)

---

# # **9. Developer Rules & Conventions**

### **1. Always keep routes thin**

* Zero business logic
* Only parameter parsing + dependency enforcement

### **2. All business logic belongs in services**

* One service file per domain

### **3. Never trust user input for org_id**

All writes must be server-injected:

```python
data["org_id"] = org_id
```

### **4. Use UUID everywhere**

We never use sequential IDs.

### **5. Always create migrations**

Never edit database schema manually.

### **6. Always update CHANGELOG.md**

Every feature or fix gets an entry.

---

# # **10. Testing Authentication**

### **1. Obtain login token**

POST → `/api/auth/login`

### **2. Press “Authorize” in Swagger**

Paste:

```
Bearer <access_token_here>
```

### **3. Add required header**

Under “Try It Out”:

```
X-Org-ID: <uuid from create-admin response>
```

---

# # **11. Git Workflow**

### **Create a feature branch**

```
git checkout -b feature/something
```

### **Commit changes**

```
git add .
git commit -m "description"
```

### **Push**

```
git push
```

### **Tag and release only from main branch**

---

# # **12. Troubleshooting**

### **“relation core.x does not exist”**

Database was not migrated.
Run:

```
docker exec -it arcoirispos_backend bash
alembic upgrade head
```

### **“401 Unauthorized”**

* Missing Bearer token
* Missing X-Org-ID header

### **“403 Forbidden”**

* Role not adequate
* Use require_admin vs require_any_staff correctly

### **“Password mismatch even after seeding”**

Hashes must be generated inside the container.

---

# # **13. Future Chapters / Extended Docs**

These will eventually become part of the Foreside Developer Handbook:

📘 Data Modeling
📘 Clean Code Transfer & Editor Hygiene
📘 Repository Hygiene (PascalCase docs)
📘 SystemHub Integration & Diagnostics
📘 Developer Security Standards
📘 Onboarding script for Mac Studio M3 Ultra

---

# # **14. Closing Notes**

The architecture is now stable, predictable, and maintainable:

* Multi-tenant
* Strong RBAC
* Clean OrgContext solution
* Verified authentication
* Fully deterministic migrations
* Predictable service-layer design
