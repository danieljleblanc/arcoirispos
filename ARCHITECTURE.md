# 🏛 ArcoírisPOS — System Architecture  
Foreside Holdings LLC  
FastAPI • PostgreSQL • React • Docker • Multi-Tenant SaaS

---

# 📘 Overview

ArcoírisPOS is a modular point-of-sale and accounting platform designed for
long-term evolution into a full business suite (“Nano Business Suite”).  
The architecture follows a **Domain-Driven Design (DDD)** pattern, dividing
business logic into clearly separated modules:

- **core** – tenant management, organizations, users, authentication  
- **pos** – terminals, sales, payments, customers  
- **inv** – items, inventory levels, stock movements  
- **acct** – journal engine, chart of accounts, balances  

Each domain module includes:

- its own routers  
- its own models  
- its own validation  
- its own service layer  
- its own migrations  

The system is engineered for modularity, extensibility, and future SaaS
deployment with multi-tenant isolation.

---

# 🧱 Layered Architecture

```
┌──────────────────────────────┐
│         Frontend (React)     │
│         UI / Client App      │
└───────────────┬──────────────┘
                │ REST / JSON
┌───────────────▼──────────────┐
│        FastAPI Backend        │
│   pos | inv | acct | core     │
│ Routers / Services / Models   │
└───────────────┬──────────────┘
                │ async SQL
┌───────────────▼──────────────┐
│           PostgreSQL          │
│  migrations | seeds | schema  │
└──────────────────────────────┘
```

This separation ensures:

- clean boundaries  
- maintainable code  
- scalable feature growth  
- ease of testing and debugging  

---

# 📁 Backend Structure (FastAPI)

```
backend/
  ├── src/
  │   ├── core/
  │   ├── pos/
  │   ├── inv/
  │   ├── acct/
  │   └── main.py
  │
  ├── database/
  │   ├── migrations/
  │   └── seeds/
  │
  ├── requirements.txt
  └── .env.example
```

### Core Backend Concepts

#### 1. **Routers**
Each domain exposes its own routes, mounted by `main.py`.

#### 2. **Models**
- Pydantic models for request/response validation  
- SQL tables for the database layer  

#### 3. **Service Layer**
Business logic is implemented in service modules, never in routers.

#### 4. **Database Layer**
- PostgreSQL  
- asyncpg  
- Domain-specific migrations  
- Strong foreign key constraints  

---

# 🗄 Database Architecture (PostgreSQL)

ArcoírisPOS uses a normalized relational model with domain isolation.

### **core/**
- organizations  
- users  
- roles  
- session/auth groundwork  

### **pos/**
- customers  
- sales  
- sale_lines  
- payments  
- tax_rates  

### **inv/**
- items  
- categories  
- stock_levels  
- stock_movements  
- locations  

### **acct/**
- chart_of_accounts  
- journal_entries  
- journal_lines  
- bank_accounts  
- balances  

The accounting subsystem uses **double-entry principles**, enabling:

- P&L  
- balance sheet  
- AR/AP  
- financial reporting  

---

# 🖥 Frontend Architecture (React)

```
frontend/
  ├── src/
  ├── public/
  ├── package.json
  └── .env.development
```

### Highlights

- Component-driven UI  
- Domain-aligned directory structure  
- Centralized API client  
- Future state: Redux or alternative state manager  
- Hot-reload dev environment  

### API Communication

```
/api/pos
/api/inv
/api/acct
/api/core
```

---

# 🐳 Docker Architecture

The system uses Docker Compose for local development.

```
docker-compose.yml
```

Includes:

- PostgreSQL  
- FastAPI API service  
- React dev server  
- Optional tooling (pgAdmin, workers)  

### Example Service Layout

```
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  db:
    image: postgres
    ports: ["5432:5432"]
```

---

# 🔐 Multi-Tenant Design (Future Phase)

The `core` module establishes the foundation for multi-tenant SaaS:

- Organization ownership  
- Role-based access  
- Tenant-aware resource isolation  

Future enhancements include:

- Row-Level Security (RLS)  
- Tenant-specific schemas  
- Billing & subscription services  
- Event-driven architecture  

---

# 🔄 Data Flow Summary

```
User → Frontend (React UI)
      → FastAPI Router
          → Service Layer
              → PostgreSQL
              ← Response
      ← UI updates
```

This ensures:

- clean separation  
- testability  
- consistency  
- clear flow of data  

---

# 🚀 Deployment Overview

### Local Development
- Docker Compose  
- Hot reload  
- Local PostgreSQL  

### Future Production Environment
- Dockerized backend + frontend builds  
- Managed PostgreSQL database (e.g., AWS RDS)  
- Nginx reverse proxy  
- CI/CD pipeline  
- Background workers (Celery or RQ)  
- Horizontal scaling with domains isolated  

---

# 🧭 Future Architecture Goals

- Full ledger-based accounting engine  
- Inventory 2.0 (purchasing workflows)  
- Payroll module  
- Timecards & attendance  
- Business intelligence engine  
- Hardware/Kiosk mode POS terminal  
- Subscription billing + invoicing  
- Cloud multi-tenant rollout  

---

# 🏁 Summary

ArcoírisPOS is engineered as a scalable, modular business platform with:

- clear domain boundaries  
- FastAPI async backend  
- React modular frontend  
- PostgreSQL relational integrity  
- Docker-powered dev environment  
- SaaS-ready architecture  

This framework will support future expansion into the full Nano Business Suite, including POS, accounting, payroll, purchasing, and advanced analytics.

