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

