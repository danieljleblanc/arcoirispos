# ⚡ Quick Start: Testing Backend in Docker

**Fastest way to get Swagger UI running and test the API**

---

## 🚀 3-Step Quick Start

### Step 1: Fix Docker Configuration (One-time)

The Docker paths have been fixed, but you may need to rebuild:

```bash
# Stop any running containers
docker-compose down

# Rebuild and start
docker-compose up --build
```

### Step 2: Run Database Migrations

```bash
# Enter backend container
docker exec -it arcoirispos_backend bash

# Run migrations (creates schema + seed data)
cd /app
alembic upgrade head

# Exit
exit
```

### Step 3: Open Swagger UI

```
http://localhost:8000/docs
```

---

## 🔑 Default Test Credentials

After running migrations, the seed data creates:

- **Email**: `admin@arcoirispos.com`
- **Password**: You'll need to check the migration file or database

To find the password:

```bash
# Option 1: Check the migration file
cat backend/src/app/infrastructure/migrations/versions/2864583ca021_seed_initial_data.py

# Option 2: Query the database
docker exec -it arcoirispos_postgres psql -U arcoiris_user -d arcoirispos_dev
SELECT email, display_name FROM core.users;
SELECT org_id, name FROM core.organizations;
\q
```

**Note**: The password hash in the migration is: `$2b$12$Vnp0Po7yFgty6yfUQFpD5O6sf5ZCZiequD2GM1l4IQhmgbB7iaG.6`

If you need to reset the password, you can:
1. Create a new user via API (if user creation endpoint exists)
2. Or manually update the database

---

## 🧪 First Test: Login

1. Open Swagger: `http://localhost:8000/docs`
2. Find `POST /auth/login`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "admin@arcoirispos.com",
     "password": "<password_from_migration_or_db>"
   }
   ```
5. Click "Execute"
6. Copy the `access_token`

---

## 🔐 Authorize in Swagger

1. Click **"Authorize"** button (top right)
2. Paste your `access_token` in the "Value" field
3. Click "Authorize"
4. Click "Close"

Now all protected endpoints will work!

---

## ✅ Verify It's Working

Test a simple endpoint:

1. Find `GET /items/` (Inventory section)
2. Click "Try it out"
3. Click "Execute"
4. Should return `200 OK` with an empty array `[]` (no items yet)

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker logs arcoirispos_backend

# Common issue: Wrong Python path
# Fix: Make sure docker-compose.yml uses: uvicorn src.app.main:app
```

### Database connection errors

```bash
# Check postgres is running
docker ps | grep postgres

# Check postgres logs
docker logs arcoirispos_postgres
```

### Migrations fail

```bash
# Check current status
docker exec -it arcoirispos_backend bash
cd /app
alembic current
alembic history

# Force upgrade
alembic upgrade head
```

### Can't login

- Verify migrations ran successfully
- Check that seed data was inserted:
  ```bash
  docker exec -it arcoirispos_postgres psql -U arcoiris_user -d arcoirispos_dev -c "SELECT email FROM core.users;"
  ```
- Try creating a new user (if endpoint exists)

---

## 📚 Next Steps

Once Swagger is working:

1. **Read the full guide**: `SWAGGER_TESTING_GUIDE.md`
2. **Test all endpoints** systematically
3. **Create test data** (items, customers, sales)
4. **Verify data integrity** in the database

---

## 🎯 Quick Test Sequence

1. ✅ Login → Get token
2. ✅ Authorize in Swagger
3. ✅ Create an item
4. ✅ List items
5. ✅ Create a customer
6. ✅ Create a sale
7. ✅ Record a payment

If all these work, your backend is fully functional! 🎉

---

*For detailed testing instructions, see `SWAGGER_TESTING_GUIDE.md`*




