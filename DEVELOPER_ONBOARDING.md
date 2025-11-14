# 🚀 ArcoírisPOS — Developer Onboarding Guide  
Foreside Holdings LLC  
FastAPI • PostgreSQL • React • Docker • Domain-Driven Architecture

---

# 📘 Overview

Welcome to the **ArcoírisPOS Development Environment**.  
This guide will walk you through:

- Project structure  
- Required tools  
- Environment setup  
- Running backend + frontend  
- Managing dependencies  
- Applying database migrations  
- Development workflow  
- Code conventions  
- Troubleshooting  

This document enables developers to go from zero → fully operational in under 10 minutes.

---

# 🧰 Prerequisites

Before you begin, install the following:

## **1. Git**
https://git-scm.com

## **2. Python 3.10+**
Use pyenv, brew, or python.org.

Check version:

```bash
python3 --version
```

## **3. Node.js (v18+) + npm**
https://nodejs.org

Check version:

```bash
node -v
npm -v
```

## **4. Docker Desktop**
Required for local development.

https://www.docker.com/products/docker-desktop

## **5. PostgreSQL Client Tools**
Useful for manual DB checks/migrations.

macOS (Homebrew):

```bash
brew install postgresql
```

---

# 📁 Project Structure

```
arcoirispos/
│
├── backend/              # FastAPI backend
│   ├── src/              # Domain modules (core, pos, inv, acct)
│   ├── database/         # SQL migrations + seeds
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/             # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docker-compose.yml    # Full dev environment
├── README.md
├── ARCHITECTURE.md
├── DATA_MODEL.md
└── API_REFERENCE.md
```

---

# 🐳 Start the Full Dev Environment (Recommended)

The easiest way to run everything is via Docker.

From project root:

```bash
docker-compose up --build
```

### Services will run at:

| Service         | URL                          |
|-----------------|------------------------------|
| FastAPI backend | http://localhost:8000        |
| API docs        | http://localhost:8000/docs   |
| React frontend  | http://localhost:3000        |
| PostgreSQL      | localhost:5432               |

Stop everything:

```bash
CTRL + C
docker-compose down
```

---

# 🐍 Backend Setup (Manual Option)

If you prefer running the backend manually:

### 1. Create environment:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# or:
.venv\Scripts\activate      # Windows
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables:

Copy the template:

```bash
cp .env.example .env
```

### 4. Run backend:

```bash
uvicorn src.main:app --reload
```

---

# ⚛️ Frontend Setup (Manual Option)

### 1. Install dependencies:

```bash
cd frontend
npm install
```

### 2. Run dev server:

```bash
npm start
```

Frontend runs at:

```
http://localhost:3000
```

---

# 🗄 Database Setup

The backend uses **PostgreSQL**.

If running locally (not Docker):

### Create DB:

```sql
CREATE DATABASE arcoirispos_dev;
CREATE USER arcoiris_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE arcoirispos_dev TO arcoiris_user;
```

### Apply migrations:

```bash
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/001_init_arcoirispos.sql
psql -U arcoiris_user -d arcoirispos_dev -f backend/database/migrations/002_indexes.sql
```

---

# 🧱 Domain Structure (Backend)

The backend follows **Domain-Driven Design (DDD)**.

Domains:

```
core/ ─ organizations, users, roles, auth
pos/  ─ sales, payments, customers
inv/  ─ items, stock, locations
acct/ ─ chart of accounts, journal engine
```

Each domain contains:

```
models/        - Pydantic + SQL models
router.py      - FastAPI route declarations
service.py     - Business logic layer
schemas.py     - Request/response schemas
```

---

# 🔄 Development Workflow

Here’s the recommended workflow when building new features.

## **1. Create a branch**

```bash
git checkout -b feature/my-feature
```

## **2. Implement changes**

Follow DDD guidelines:

- Add models to domain folder  
- Add routers only for HTTP endpoints  
- Put business logic in services  
- Add migration if DB changes  

## **3. Run tests (future)**

Test suite will be added soon.

## **4. Commit changes**

```bash
git add .
git commit -m "Add new feature"
```

## **5. Push branch**

```bash
git push origin feature/my-feature
```

## **6. Open Pull Request**

Submit PR to `main` for review.

---

# 🧪 Code Conventions

### **Python / FastAPI**
- snake_case for variables and functions  
- PascalCase for classes  
- Keep routers thin  
- Services contain all business logic  
- Use Pydantic for validation  
- Avoid inline SQL (use prepared statements or SQL files)  

### **React**
- Component per file  
- Hooks for state management  
- Keep UI logic separate from APIs  
- Use `.env.development` for API URL  

### **SQL**
- Use UUID primary keys  
- Enforce foreign keys  
- No nullable values unless required  
- Follow naming: `org_id`, `item_id`, etc.  

---

# 🛠 Dependency Management

### Backend
```bash
pip freeze > requirements.txt
```

### Frontend
```bash
npm install <pkg>
npm run build
```

### Docker
Rebuild if dependencies change:

```bash
docker-compose build
```

---

# 🧯 Troubleshooting

## Backend fails to start:
- Missing `.env` file  
- PostgreSQL not running  
- Wrong DB URL  
- Migration missing  

## Frontend shows blank page:
- Wrong API URL  
- CORS errors  
- Backend not running  

## Docker won’t start:
- Port already in use (`8000` or `5432`)  
- Remove existing containers:

```bash
docker-compose down -v
```

## Database errors:
- Run migrations again  
- Drop + recreate DB in dev environments:

```sql
DROP DATABASE arcoirispos_dev;
CREATE DATABASE arcoirispos_dev;
```

---

# 🔮 Future Developer Tools

- Full test suite  
- Pre-commit hooks  
- CI/CD pipeline  
- Swagger → Markdown automated docs  
- Background worker container  
- Local seed data loader  

---

# 🏁 Summary

This onboarding guide gives developers everything they need to:

- run ArcoírisPOS locally  
- understand project structure  
- follow development conventions  
- contribute safely  
- troubleshoot common issues  

ArcoírisPOS is built to scale into the full Nano Business Suite, and this onboarding guide ensures team members can contribute confidently and consistently.

