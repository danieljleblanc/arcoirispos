# 🧪 ArcoírisPOS — Swagger Testing Guide
**Complete guide to testing the backend API in Docker using Swagger UI**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Setup & Fixes](#docker-setup--fixes)
3. [Accessing Swagger UI](#accessing-swagger-ui)
4. [Authentication Flow](#authentication-flow)
5. [Testing Endpoints](#testing-endpoints)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## 🚀 Quick Start

### Step 1: Start Docker Services

```bash
# From project root
docker-compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- React frontend (port 3000)

### Step 2: Run Database Migrations

Once containers are running, apply migrations:

```bash
# Enter the backend container
docker exec -it arcoirispos_backend bash

# Run migrations
cd /app
alembic upgrade head

# Exit container
exit
```

### Step 3: Access Swagger UI

Open your browser to:
```
http://localhost:8000/docs
```

You should see the Swagger UI with all available endpoints.

---

## 🔧 Docker Setup & Fixes

### Issue: Dockerfile Path Problems

The current `Dockerfile` and `docker-compose.yml` have incorrect paths. Here are the fixes needed:

#### Fix 1: Update Dockerfile

The Dockerfile tries to run `uvicorn src.main:app` but the actual path is `src/app/main.py`.

**Current (incorrect):**
```dockerfile
CMD ["bash", "-c", "python wait_for_db.py && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]
```

**Should be:**
```dockerfile
CMD ["bash", "-c", "uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload"]
```

#### Fix 2: Update docker-compose.yml

**Current (incorrect):**
```yaml
command: >
  bash -c "python src/wait_for_db.py &&
  uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
```

**Should be:**
```yaml
command: >
  bash -c "uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload"
```

#### Fix 3: Create .env file (if missing)

The Dockerfile expects a `.env` file. Create one in `/backend/`:

```bash
cd backend
cat > .env << EOF
SECRET_KEY=dev-secret-key-change-me-in-production
DATABASE_URL=postgresql://arcoiris_user:ArcoirisDevP%40ss2025@postgres:5432/arcoirispos_dev
DATABASE_URL_ASYNC=postgresql+asyncpg://arcoiris_user:ArcoirisDevP%40ss2025@postgres:5432/arcoirispos_dev
EOF
```

---

## 🌐 Accessing Swagger UI

### Swagger UI URL
```
http://localhost:8000/docs
```

### Alternative: ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI JSON Schema
```
http://localhost:8000/openapi.json
```

---

## 🔐 Authentication Flow

### Overview

The API uses **JWT Bearer tokens** for authentication. Most endpoints require:
1. **Authorization header**: `Bearer <access_token>`
2. **X-Org-ID header**: Organization UUID (for multi-tenant context)

### Step-by-Step Authentication

#### 1. Get Test User Credentials

After running migrations, check the seed data for the default admin user:

```bash
# Connect to database
docker exec -it arcoirispos_postgres psql -U arcoiris_user -d arcoirispos_dev

# Check users
SELECT email, display_name FROM core.users;

# Check organizations
SELECT org_id, name FROM core.organizations;

# Exit
\q
```

**Default credentials** (from seed migration):
- Email: `admin@arcoirispos.com`
- Password: `Admin123!` (check the migration file for actual hash)

#### 2. Login via Swagger

1. Open Swagger UI: `http://localhost:8000/docs`
2. Find the **`/auth/login`** endpoint
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "email": "admin@arcoirispos.com",
     "password": "Admin123!"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` from the response

#### 3. Authorize in Swagger

1. Click the **"Authorize"** button at the top of Swagger UI
2. In the "Value" field, paste your `access_token` (without "Bearer")
3. Click "Authorize"
4. Click "Close"

Now all protected endpoints will automatically include the token!

#### 4. Set Organization Header

For endpoints that require `X-Org-ID`:

1. Get your organization UUID from the database query above
2. In Swagger, look for the endpoint you want to test
3. You'll need to manually add the header (Swagger may not show it in the UI)
4. Or use the "Try it out" feature and look for header fields

**Note:** The current implementation uses a temporary placeholder org context, so this may not be strictly required yet.

---

## 🧪 Testing Endpoints

### Available Endpoint Groups

Based on the current codebase:

#### **Authentication** (`/auth`)
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token

#### **Inventory** (`/items`, `/locations`, etc.)
- `GET /items/` - List items
- `POST /items/` - Create item
- `GET /items/{item_id}` - Get item
- `PATCH /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

Similar patterns for:
- `/locations`
- `/stock-levels`
- `/stock-movements`
- `/admin-stock-adjust`

#### **POS** (`/customers`, `/sales`, etc.)
- `GET /customers/` - List customers
- `POST /customers/` - Create customer
- `GET /sales/` - List sales
- `POST /sales/` - Create sale (checkout)
- `GET /sales/{sale_id}` - Get sale with lines/payments
- `POST /payments/` - Record payment
- `GET /tax-rates/` - List tax rates
- `POST /tax-rates/` - Create tax rate

### Example: Creating an Item

1. **Authorize first** (see Authentication Flow above)

2. **Navigate to** `POST /items/`

3. **Click "Try it out"**

4. **Enter request body:**
   ```json
   {
     "name": "Test Product",
     "sku": "TEST-001",
     "price": 19.99,
     "cost": 10.00,
     "track_stock": true
   }
   ```

5. **Click "Execute"**

6. **Check response:**
   - Status: `201 Created`
   - Response body should contain the created item with `item_id`

### Example: Creating a Sale

1. **First, create an item** (see above) and note the `item_id`

2. **Create a customer** (optional):
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com"
   }
   ```
   Note the `customer_id` from response

3. **Create a sale:**
   ```json
   {
     "customer_id": "<customer_id_from_step_2>",
     "terminal_id": null,
     "sale_lines": [
       {
         "item_id": "<item_id_from_step_1>",
         "quantity": 2,
         "unit_price": 19.99
       }
     ],
     "tax_amount": 3.20,
     "discount_amount": 0
   }
   ```

4. **Check response** - should include:
   - `sale_id`
   - `subtotal`, `tax_amount`, `total`
   - `sale_lines` array
   - `payments` array (empty initially)

### Example: Recording a Payment

1. **Get a sale_id** from a previous sale

2. **Navigate to** `POST /payments/`

3. **Enter request body:**
   ```json
   {
     "sale_id": "<sale_id>",
     "payment_method": "card",
     "amount": 43.18,
     "reference": "TXN-12345"
   }
   ```

4. **Execute** - payment should be recorded

---

## 🐛 Common Issues & Solutions

### Issue 1: "Connection refused" or "Service unavailable"

**Solution:**
```bash
# Check if containers are running
docker ps

# Check logs
docker logs arcoirispos_backend
docker logs arcoirispos_postgres

# Restart services
docker-compose restart
```

### Issue 2: "401 Unauthorized" on protected endpoints

**Solution:**
- Make sure you've logged in and copied the `access_token`
- Click "Authorize" in Swagger and paste the token
- Verify the token hasn't expired (default: 15 minutes)

### Issue 3: "404 Not Found" for endpoints

**Solution:**
- Check that migrations have run: `alembic upgrade head`
- Verify the endpoint path matches what's in Swagger
- Check backend logs for routing errors

### Issue 4: "500 Internal Server Error"

**Solution:**
```bash
# Check backend logs
docker logs arcoirispos_backend

# Common causes:
# - Database connection issues
# - Missing required fields in request
# - Validation errors
```

### Issue 5: Database connection errors

**Solution:**
```bash
# Verify postgres is healthy
docker ps | grep postgres

# Check database exists
docker exec -it arcoirispos_postgres psql -U arcoiris_user -l

# Restart postgres
docker-compose restart postgres
```

### Issue 6: "Module not found" errors

**Solution:**
- The Dockerfile path issue mentioned above
- Rebuild containers: `docker-compose up --build --force-recreate`

### Issue 7: Migrations fail

**Solution:**
```bash
# Enter backend container
docker exec -it arcoirispos_backend bash

# Check current migration status
alembic current

# Check migration history
alembic history

# Force upgrade
alembic upgrade head
```

---

## 📊 Testing Checklist

Use this checklist to systematically test the API:

### Authentication
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Refresh token works
- [ ] Protected endpoint requires auth (try without token)

### Inventory Module
- [ ] List items (GET /items/)
- [ ] Create item (POST /items/)
- [ ] Get item by ID (GET /items/{id})
- [ ] Update item (PATCH /items/{id})
- [ ] Delete item (DELETE /items/{id})
- [ ] List locations
- [ ] Create location
- [ ] List stock levels
- [ ] Create stock movement

### POS Module
- [ ] List customers
- [ ] Create customer
- [ ] List sales
- [ ] Create sale (checkout)
- [ ] Get sale with lines/payments
- [ ] Record payment
- [ ] List tax rates
- [ ] Create tax rate

### Error Handling
- [ ] Invalid request body returns 422
- [ ] Missing required field returns 422
- [ ] Non-existent resource returns 404
- [ ] Unauthorized access returns 401

---

## 🔍 Advanced Testing Tips

### 1. Using cURL (Alternative to Swagger)

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@arcoirispos.com", "password": "Admin123!"}'

# Save token
TOKEN="<paste_access_token_here>"

# Use token for protected endpoint
curl -X GET "http://localhost:8000/items/" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Testing with Postman/Insomnia

1. Import OpenAPI schema: `http://localhost:8000/openapi.json`
2. Set up environment variables:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (from login)
3. Use collection runner for automated tests

### 3. Database Inspection

```bash
# Connect to database
docker exec -it arcoirispos_postgres psql -U arcoiris_user -d arcoirispos_dev

# Useful queries:
SELECT * FROM inv.items;
SELECT * FROM pos.sales;
SELECT * FROM pos.customers;
SELECT * FROM core.users;
SELECT * FROM core.organizations;

# Exit
\q
```

---

## 📝 Next Steps

After successfully testing in Swagger:

1. **Document any bugs** you find
2. **Test edge cases** (empty strings, negative numbers, etc.)
3. **Verify data integrity** (check database after operations)
4. **Test error scenarios** (invalid IDs, missing fields)
5. **Performance testing** (if needed, with tools like Apache Bench)

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check backend logs: `docker logs arcoirispos_backend`
2. Check database logs: `docker logs arcoirispos_postgres`
3. Review the code in `backend/src/app/`
4. Check migration files in `backend/src/app/infrastructure/migrations/`

---

*Last Updated: 2025-01-XX*




