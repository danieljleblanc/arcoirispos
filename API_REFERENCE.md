# 📚 ArcoírisPOS — API Reference  
Foreside Holdings LLC  
FastAPI • PostgreSQL • Modular REST API

---

# 📘 Overview

This document provides a complete reference for the ArcoírisPOS API endpoints, grouped by domain:

- **CORE** — organizations, users, authentication  
- **POS** — sales, customers, payments  
- **INVENTORY (INV)** — items, stock, locations  
- **ACCOUNTING (ACCT)** — chart of accounts, journal entries, ledger  

All endpoints follow these conventions:

- REST-based  
- JSON request/response  
- Standard HTTP methods: GET, POST, PUT, PATCH, DELETE  
- Consistent status codes  
- All timestamps returned in ISO 8601 UTC  

Authentication model (future):  
- OAuth2 / JWT Bearer tokens

---

# 🔐 Authentication (Future)

Authentication is not yet active but planned.

Standard workflow will be:

```
POST /api/core/auth/login
→ returns access_token (JWT)
Authorization: Bearer <token>
```

All protected endpoints will ultimately require an Authorization header.

---

# 🧩 CORE API  
## Base Path: `/api/core`

---

## 📌 **1. Organizations**

### **GET /api/core/organizations**
Returns all organizations (admin only in future).

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Foreside Holdings",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

### **POST /api/core/organizations**
Create a new organization.

**Body:**
```json
{
  "name": "My Business"
}
```

---

## 📌 **2. Users**

### **GET /api/core/users**
List all users (scoped by organization).

### **POST /api/core/users**
Create a new user.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "MySecret123",
  "role": "admin"
}
```

---

# 🧩 POS API  
## Base Path: `/api/pos`

---

## 👤 **1. Customers**

### **GET /api/pos/customers**
Returns a list of customers.

### **POST /api/pos/customers**
Create a new customer.

**Body:**
```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-555-1212"
}
```

---

## 🧾 **2. Sales**

### **GET /api/pos/sales**
List sales records.

### **POST /api/pos/sales**
Create a sale including one or more line items.

**Body Example:**
```json
{
  "customer_id": "uuid",
  "items": [
    { "item_id": "uuid", "quantity": 2, "unit_price": 10.00 }
  ],
  "tax": 1.75,
  "total": 21.75
}
```

---

## 🧾 **3. Sale Lines**

### **GET /api/pos/sales/{sale_id}/lines**
Get all line items for a sale.

---

## 💳 **4. Payments**

### **POST /api/pos/payments**
Record a payment for a sale.

**Body:**
```json
{
  "sale_id": "uuid",
  "method": "card",
  "amount": 21.75
}
```

---

## 💼 **5. Tax Rates**

### **GET /api/pos/tax-rates**
List tax rates for the organization.

### **POST /api/pos/tax-rates**
Add a tax rate.

---

# 📦 INVENTORY (INV) API  
## Base Path: `/api/inv`

---

## 📦 **1. Items**

### **GET /api/inv/items**
List items.

### **POST /api/inv/items**
Create a new inventory item.

**Body:**
```json
{
  "name": "Notebook",
  "sku": "SKU-001",
  "price": 9.99,
  "cost": 5.00,
  "track_stock": true
}
```

---

## 🏬 **2. Locations**

### **GET /api/inv/locations**

### **POST /api/inv/locations**

**Body:**
```json
{
  "name": "Main Warehouse",
  "type": "warehouse"
}
```

---

## 📊 **3. Stock Levels**

### **GET /api/inv/stock-levels**
Returns all stock levels for the organization.

### **GET /api/inv/stock-levels/{item_id}**
Returns stock levels for a specific item.

---

## 🔄 **4. Stock Movements**

### **POST /api/inv/stock-movements**
Record an inventory adjustment.

**Body:**
```json
{
  "item_id": "uuid",
  "location_id": "uuid",
  "quantity_change": -1,
  "reason": "sale"
}
```

---

# 🧮 ACCOUNTING (ACCT) API  
## Base Path: `/api/acct`

---

## 🧭 **1. Chart of Accounts**

### **GET /api/acct/accounts**
Returns all ledger accounts.

### **POST /api/acct/accounts**

**Body:**
```json
{
  "code": "1000",
  "name": "Cash on Hand",
  "type": "asset"
}
```

---

## 📘 **2. Journal Entries**

### **GET /api/acct/journal-entries**

### **POST /api/acct/journal-entries**
Creates a double-entry journal transaction.

**Body Example:**
```json
{
  "entry_date": "2025-07-10",
  "memo": "Daily Sales Batch",
  "lines": [
    { "account_id": "uuid", "debit": 100.00, "credit": 0 },
    { "account_id": "uuid", "debit": 0, "credit": 100.00 }
  ]
}
```

Constraints:
- Debits must equal credits  
- At least two lines required  

---

## 🏦 **3. Bank Accounts**

### **GET /api/acct/bank-accounts**

### **POST /api/acct/bank-accounts**

---

# 📡 Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Errors:

```json
{
  "success": false,
  "error": {
    "message": "Item not found",
    "code": "NOT_FOUND"
  }
}
```

---

# 📘 Pagination Format (Future)

```
GET /api/pos/sales?page=2&limit=50
```

Response:

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total_pages": 10,
    "total_items": 500
  }
}
```

---

# 🧪 Status Codes

- **200 OK** — success  
- **201 Created** — resource created  
- **400 Bad Request** — validation error  
- **401 Unauthorized** — missing/invalid credentials  
- **403 Forbidden** — lack of role permission  
- **404 Not Found** — resource missing  
- **409 Conflict** — duplicate SKU/email/account code  
- **500 Server Error** — unexpected backend failure  

---

# 🔮 Future APIs

Planned expansions include:

### **Inventory 2.0**
- Purchase Orders  
- Vendor Management  

### **POS 2.0**
- Shift Management  
- Drawer Balancing  

### **Accounting 2.0**
- AR/AP  
- Recurring Entries  
- Reconciliation Engine  

### **Admin APIs**
- Organization billing  
- Subscription management  
- Audit logs  

---

# 🏁 Summary

This API reference defines the current and future structure of the ArcoírisPOS REST API.  
It ensures consistent development, scalable feature growth, and accurate integration with frontend and external systems.

As the project evolves, this document should be updated alongside each new module, endpoint, or domain release.

