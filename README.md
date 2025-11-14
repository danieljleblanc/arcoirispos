---

# 📄 **README.md (ArcoírisPOS — Full Version)**

```markdown
# 🌈 ArcoírisPOS  
### A Modular Point-of-Sale + Accounting System (FastAPI • PostgreSQL • React)

ArcoírisPOS is the foundation of a long-term, multi-module business suite designed
to grow into a full accounting platform and QuickBooks Online competitor.  
The architecture emphasizes:

- Clean separation of POS, Inventory, Core, and Accounting domains  
- FastAPI backend with async PostgreSQL  
- React frontend  
- Docker-based local development  
- Multi-tenant SaaS structure  
- Enterprise-ready data model (double-entry accounting)  

---

# 🧱 Project Structure

```

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

````

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/arcoirispos.git
cd arcoirispos
````

---

# 🐳 Docker-Based Local Development

This project uses **Docker Compose** for:

* PostgreSQL
* FastAPI backend
* React development server

To start everything:

```bash
docker-compose up --build
```

### Services will be available at:

| Service        | URL                                                      |
| -------------- | -------------------------------------------------------- |
| FastAPI        | [http://localhost:8000](http://localhost:8000)           |
| API Docs       | [http://localhost:8000/docs](http://localhost:8000/docs) |
| React Frontend | [http://localhost:3000](http://localhost:3000)           |
| PostgreSQL     | localhost:5432                                           |

---

# 🗄 Database Setup (PostgreSQL)

If running manually (not through Docker):

```sql
CREATE DATABASE arcoirispos_dev;
CREATE USER arcoiris_user WITH PASSWORD 'YourSecurePassword';
GRANT ALL PRIVILEGES ON DATABASE arcoirispos_dev TO arcoiris_user;
```

Run migrations:

```bash
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/001_init_arcoirispos.sql
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/002_indexes.sql
```

---

# 🐍 Backend (FastAPI)

## Run Backend Manually (Alternative to Docker)

Create virtual environment:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run server:

```bash
uvicorn src.main:app --reload
```

---

# ⚛️ Frontend (React)

From the `frontend/` directory:

```bash
npm install
npm start
```

This launches the development server at:

```
http://localhost:3000
```

---

# 🧮 Data Model Overview

ArcoírisPOS includes a full PostgreSQL schema across 4 main domains:

### **core/**

* Organizations (multi-tenant)
* Users & Roles
* Authentication & session future support

### **pos/**

* Customers
* Terminals
* Sales
* Sale Lines
* Payments
* Tax Rates

### **inv/**

* Items
* Locations
* Stock Levels
* Stock Movements

### **acct/**

* Chart of Accounts
* Journal Entries
* Journal Lines
* Bank Accounts
* Customer Balances

SQL migrations included in `/backend/database/migrations`.

---

# 📦 Environment Variables

Backend `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://arcoiris_user:password@localhost:5432/arcoirispos_dev
SECRET_KEY=replace_with_secure_key
```

Frontend `.env.development`:

```env
REACT_APP_API_URL=http://localhost:8000
```

Copy these files and remove the `.example` suffix to activate.

---

# 🔭 Project Roadmap

### Phase 1 — Foundation

✔ Data model
✔ POS basics (sales, customers, items)
✔ Docker environment
✔ FastAPI scaffold

### Phase 2 — Operational POS

* Inventory v1
* Payments integration
* Basic reporting
* Shift/cash drawer tools

### Phase 3 — Accounting Engine

* Ledger + journal system
* Chart of accounts
* AR/AP syncing
* P&L, Balance Sheet

### Phase 4 — SaaS Platform

* Multi-tenant isolation
* Subscription billing
* Notifications
* Event bus architecture

### Phase 5 — Nano Business Suite

* Payroll
* Timecards
* Purchasing
* Inventory 2.0
* Business intelligence

### Phase 6 — Hardware & Enterprise

* Branded POS terminals
* Kiosk mode OS
* In-house payment processor
* App marketplace

---

# 🧑‍💻 Contributing

To contribute:

```bash
git checkout -b feature/my-feature
# make changes
git commit -m "Add new feature"
git push origin feature/my-feature
```

Then submit a Pull Request.

---

# 🛡 License

To be added.

---

# 🌟 Author

**Daniel Joseph LeBlanc**
Foreside Holdings LLC / ArcoírisPOS Project
FastAPI • PostgreSQL • React • System Architecture

```

---