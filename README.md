# 🌈 ArcoírisPOS  
### Modular Point-of-Sale (POS) + Accounting System  
**FastAPI • PostgreSQL • React • Docker • Multi-Tenant Architecture**

<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow?style=flat-square" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-316192?style=flat-square" />
  <img src="https://img.shields.io/badge/Frontend-React-00d8ff?style=flat-square" />
  <img src="https://img.shields.io/badge/License-Proprietary-lightgrey?style=flat-square" />
</p>

---

# 📘 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Clone the Repository](#1-clone-the-repository)
  - [Docker Development](#docker-based-local-development)
  - [Manual Backend Setup](#backend-fastapi)
  - [Manual Frontend Setup](#frontend-react)
- [Database Schema](#🧮-data-model-overview)
- [Environment Variables](#📦-environment-variables)
- [Roadmap](#🔭-project-roadmap)
- [Contributing](#🧑‍💻-contributing)
- [License](#🛡-license)
- [Author](#🌟-author)

---

# 🧭 Overview

**ArcoírisPOS** is a multi-module Point-of-Sale and Accounting platform designed for:

- retail businesses  
- restaurants  
- service organizations  
- SaaS deployments  
- enterprise-grade bookkeeping integrations  

Its long-term goal is to evolve into a full accounting platform and a direct competitor to **QuickBooks Online**, with a strong emphasis on:

- modular design  
- multi-tenant organization management  
- a clean, extensible architecture  
- enterprise-ready data model  

---

# ✨ Features

### POS Core
- Customers, items, terminals  
- Sales, sale lines, payment handling  
- Taxes, discounts, and promotions  

### Inventory Management
- Items & categories  
- Stock levels & movements  
- Location-based multi-store tracking  

### Accounting Engine (In Progress)
- Double-entry ledger  
- Chart of accounts  
- Journal entries & lines  
- AR/AP foundations  

### Developer-Friendly
- Full local Docker environment  
- Hot-reload FastAPI backend  
- Hot-reload React frontend  
- SQL-based migration system  
- Clean modular separation: `pos/`, `inv/`, `acct/`, `core/`  

---

# 🛠 Technology Stack

| Layer       | Technology                 |
|-------------|-----------------------------|
| Backend     | FastAPI (Python 3.10+)      |
| Database    | PostgreSQL (asyncpg)        |
| Frontend    | React (CRA / Vite optional) |
| DevOps      | Docker + Docker Compose     |
| Auth        | JWT / OAuth2                |
| Architecture| Domain-Driven Design (DDD)  |

---

# 🏗 Architecture Overview

Below is a conceptual structure of the system:

```
┌──────────────────────────────┐
│          Frontend            │
│          (React)             │
└───────────────┬──────────────┘
                │ REST / JSON
┌───────────────▼──────────────┐
│        FastAPI Backend        │
│  pos | inv | core | acct      │
└───────────────┬──────────────┘
                │ SQL / Async
┌───────────────▼──────────────┐
│           PostgreSQL          │
│  migrations | seeds | schemas │
└──────────────────────────────┘
```

The project follows **domain partitioning**, separating business logic into clean modules:

- `core/` — organizations, users, auth  
- `pos/` — customer, sales, payments  
- `inv/` — stock & item management  
- `acct/` — journal / ledger engine  

---

# 🧱 Project Structure

````markdown
arcoirispos/
│
├── docker-compose.yml
├── README.md
├── .gitignore
│
├── backend/
│   ├── src/
│   │   ├── core/
│   │   ├── pos/
│   │   ├── inv/
│   │   ├── acct/
│   │   └── main.py
│   │
│   ├── database/
│   │   ├── migrations/
│   │   │   ├── 001_init_arcoirispos.sql
│   │   │   ├── 002_indexes.sql
│   │   └── seeds/
│   │       └── demo_data.sql
│   │
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── .env.development
    
    **Daniel Joseph LeBlanc**  
Foreside Holdings LLC  
Architect • Developer • Designer  
FastAPI • PostgreSQL • React • Systems Engineering

# **ArcoirisPOS Database Migration Graph & Documentation**

This document provides a **complete overview** of the Alembic migration sequence for the ArcoirisPOS backend. It includes a visual graph of the migration chain, detailed descriptions of each revision, and rules for maintaining the migration integrity going forward.

---

## **📌 Purpose of This Document**

* Establish the *canonical* migration order
* Prevent out-of-sequence migrations
* Document how the baseline collapse works
* Help future developers understand which migrations create schemas, tables, test stubs, and seed data
* Provide a safe workflow for adding new migrations

---

# **📈 Migration Graph (ASCII / Markdown Visual)**

```text
                       ┌──────────────────────────────┐
                       │        BASELINE START         │
                       │      (no revision present)    │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                         ┌────────────────────────────┐
                         │ 000000000001                │
                         │ Full Schema Baseline        │
                         │ baseline_schema_collapse.py │
                         └───────────────┬────────────┘
                                         │
                                         ▼
                         ┌────────────────────────────┐
                         │ 37a02ec8662a                │
                         │ Init Schema                 │
                         │ init_schema.py              │
                         └───────────────┬────────────┘
                                         │
                                         ▼
                         ┌────────────────────────────┐
                         │ 853113448960               │
                         │ Template Sanity Test       │
                         │ template_sanity_test.py    │
                         └───────────────┬────────────┘
                                         │
                                         ▼
                         ┌────────────────────────────┐
                         │ 2864583ca021               │
                         │ Seed Initial Data          │
                         │ seed_initial_data.py       │
                         └────────────────────────────┘
```

---

# **📄 Migration Revision Index**

| Order | Revision ID    | File Name                     | Description                                                            |
| ----: | -------------- | ----------------------------- | ---------------------------------------------------------------------- |
|     0 | *BASE*         | *no file*                     | Empty state before first migration                                     |
|     1 | `000000000001` | `baseline_schema_collapse.py` | Creates schemas & extensions only. This is the new canonical baseline. |
|     2 | `37a02ec8662a` | `init_schema.py`              | Full table & enum creation (core, acct, inv, pos).                     |
|     3 | `853113448960` | `template_sanity_test.py`     | No-op template migration (kept for history).                           |
|     4 | `2864583ca021` | `seed_initial_data.py`        | Inserts initial org/user/role/etc.                                     |

---

# **📌 Baseline Migration Behavior**

### The file `000000000001_baseline_schema_collapse.py`:

* **MUST remain minimal**
  ✔ Creates schemas
  ✔ Creates required extensions (`citext`, `pgcrypto`)
  ✘ **No tables**
  ✘ **No enums**
  ✘ **No foreign keys**
  ✘ **No sequences or seed data**

This ensures Alembic can:

* downgrade safely to baseline
* rebase future schemas
* allow clean rebuilds without reinitializing table content

---

# **🚀 Commands to Work With the Migration Graph**

### **Upgrade to latest**

```bash
alembic upgrade head
```

### **Downgrade to baseline**

```bash
alembic downgrade 000000000001
```

### **Downgrade ALL the way (dangerous)**

```bash
alembic downgrade base
```

### **Show the migration tree**

```bash
alembic history --verbose
```

---

# **📐 Rules for Future Migrations**

To keep the system stable:

### ✔ DO:

* Create new migrations using:

  ```bash
  alembic revision -m "description"
  ```
* Keep baseline **untouched forever**
* Place all schema changes in migrations **after** `37a02ec8662a`
* Ensure each migration:

  * is reversible
  * does not duplicate prior schema objects
  * maintains referential integrity

### ✘ DO NOT:

* Modify old migration files
* Add tables or types to the baseline
* Change revision IDs
* Change down_revision links retroactively
* Manually alter database schema outside Alembic

---

# **⚠️ Developer Warnings (Critical)**

### **1. Never rebuild the baseline again.**

This is a one-time operation.
The new canonical base is now `000000000001`.

### **2. Do not reorder migration history.**

Alembic depends on a strict DAG.

### **3. All future schema work MUST start after `37a02ec8662a`.**

### **4. If autogenerate ever outputs an empty migration:**

It should be automatically discarded (your env.py handles this).

### **5. If a migration fails during CI or local build:**

Run:

```bash
docker-compose down -v
docker-compose up -d
alembic upgrade head
```



