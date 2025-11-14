# 📊 ArcoírisPOS — Data Model Documentation  
Foreside Holdings LLC  
PostgreSQL • FastAPI • Domain-Driven Schema • Double-Entry Accounting

---

# 📘 Overview

This document describes the **entire relational data model** for ArcoírisPOS.  
The system is structured using:

- **Domain-Driven Design (DDD)**  
- **Normalized relational modeling (3NF)**  
- **Strict foreign key enforcement**  
- **Clear separation of POS, Inventory, Accounting, and Core domains**  
- **Future-ready multi-tenant architecture**  

This data model is the backbone for point-of-sale operations, inventory control, and the future accounting engine powering the Nano Business Suite.

---

# 🧱 Domain Overview

ArcoírisPOS is divided into four major domains:

```
core ─ Organizations, Users, Roles
pos  ─ Sales, Payments, Customers
inv  ─ Items, Stock, Movements, Locations
acct ─ Ledger, COA, Journal Entries
```

Each domain contains **entities**, **relationships**, and **migrations** scoped to its functional boundaries.

---

# 🏛 High-Level ERD (Entity Relationship Diagram)

```
                   ┌─────────────────────┐
                   │     organizations   │
                   └───────────┬─────────┘
                               │ 1:N
                     ┌─────────▼──────────┐
                     │        users        │
                     └─────────┬──────────┘
                               │ 1:N
               ┌───────────────▼───────────────┐
               │           customers            │
               └───────┬───────────────────────┘
                       │ 1:N
        ┌──────────────▼──────────────┐      1:N
        │             sales            │───────────────┐
        └───────┬────────────┬────────┘               │
                │ 1:N         │ 1:N                    │
   ┌────────────▼───────┐ ┌───▼──────────┐      ┌─────▼─────────┐
   │      sale_lines     │ │   payments   │      │    tax_rates   │
   └──────────┬──────────┘ └──────────────┘      └────────────────┘
              │ N:1
   ┌──────────▼─────────┐
   │       items         │
   └─────────┬──────────┘
             │ 1:N
     ┌───────▼─────────────┐
     │     stock_levels     │
     └─────────┬────────────┘
               │ 1:N
        ┌──────▼──────────────┐
        │   stock_movements   │
        └─────────────────────┘


        Accounting Domain (Double-Entry)

     ┌──────────────┐      1:N      ┌────────────────┐
     │ chart_of_accts│◄─────────────│ journal_entries│
     └───────┬──────┘               └──────────┬─────┘
             │ 1:N                                │ 1:N
       ┌─────▼───────────────┐          ┌────────▼───────────┐
       │     journal_lines    │─────────►│   bank_accounts    │
       └──────────────────────┘   N:1    └────────────────────┘
```

---

# 🧩 Domain: CORE

## **1. organizations**
Defines multi-tenant ownership.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| name | text | required |
| created_at | timestamp | default now() |
| updated_at | timestamp | auto-updated |

Indexes:
- PK on id  
- Unique index on name

---

## **2. users**
Belong to organizations.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK → organizations.id |
| email | text | unique |
| hashed_password | text | required |
| role | text | enum-like |
| created_at | timestamp | default now() |

Constraints:
- Users cannot exist without an org  
- Email unique within system  

---

# 🧩 Domain: POS

## **1. customers**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| name | text | required |
| email | text | optional |
| phone | text | optional |
| created_at | timestamp | default now() |

Indexes:
- Email (non-unique)
- Name (non-unique)

---

## **2. sales**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| customer_id | UUID | FK → customers.id |
| sale_date | timestamp | required |
| subtotal | numeric | required |
| tax | numeric | required |
| total | numeric | required |
| status | text | ENUM("open", "completed", "void") |
| created_at | timestamp | default now() |

Relationships:
- One sale has many sale_lines  
- One sale can have many payments  

---

## **3. sale_lines**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| sale_id | UUID | FK → sales.id |
| item_id | UUID | FK → items.id |
| quantity | numeric | required |
| unit_price | numeric | required |
| line_total | numeric | calculated |

Indexes:
- sale_id  
- item_id  

---

## **4. payments**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| sale_id | UUID | FK |
| method | text | ENUM("cash", "card", "other") |
| amount | numeric | required |
| paid_at | timestamp | default now() |

---

## **5. tax_rates**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| name | text | e.g., “CA State Tax” |
| rate | numeric | e.g., 0.0875 |
| active | boolean | default true |

---

# 🧩 Domain: INVENTORY (inv)

## **1. items**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| name | text | required |
| sku | text | unique optional |
| price | numeric | default = 0 |
| cost | numeric | optional |
| track_stock | boolean | default true |
| active | boolean | default true |

---

## **2. stock_levels**

Tracks the current quantity at each location.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| item_id | UUID | FK |
| location_id | UUID | FK |
| quantity | numeric | required |

Constraint:
- Unique (item_id, location_id)

---

## **3. stock_movements**

Transactional history (never overwritten).

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| item_id | UUID | FK |
| location_id | UUID | FK |
| quantity_change | numeric | +inbound, -outbound |
| reason | text | purchase/sale/adjustment |
| occurred_at | timestamp | default now() |

---

## **4. locations**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| name | text | required |
| type | text | store/warehouse/etc |

---

# 🧩 Domain: ACCOUNTING (acct)

The accounting module is a **double-entry general ledger system**.

## **1. chart_of_accounts**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| code | text | unique per org |
| name | text | required |
| type | text | asset/liability/equity/income/expense |

---

## **2. journal_entries**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| entry_date | date | required |
| memo | text | optional |
| created_by | UUID | FK → users.id |

---

## **3. journal_lines**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| entry_id | UUID | FK → journal_entries.id |
| account_id | UUID | FK → chart_of_accounts.id |
| debit | numeric | default 0 |
| credit | numeric | default 0 |

Constraint:
- Sum(debits) must equal Sum(credits) within each journal_entry  

---

## **4. bank_accounts**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| org_id | UUID | FK |
| name | text | e.g., “Main Checking” |
| account_id | UUID | FK → chart_of_accounts.id |
| balance | numeric | computed or cached |

---

# 🧮 Naming Conventions

### Tables
- snake_case  
- singular nouns: `sale`, `payment`, `item`  

### Primary Keys
- UUID (v4)  
- Named `id`  

### Foreign Keys
- `xxx_id` convention  

### Timestamps
- `created_at`  
- `updated_at`  
- `occurred_at` for event-like tables  

---

# 🔐 Multi-Tenant Data Model Notes

ArcoírisPOS is structured for future multi-tenant operation:

- Every business entity includes `org_id`  
- Future schema: per-tenant Row-Level Security (RLS)  
- Database isolation possible by:
  - shared schema + RLS  
  - schema-per-tenant  
  - database-per-tenant (enterprise scale)  

---

# 🚀 Future Expansion

### Inventory 2.0
- Purchase Orders  
- Goods Receipts  
- Vendor Management  

### Accounting 2.0
- AR/AP  
- Recurring entries  
- Payroll journal automation  

### POS 2.0
- Shift management  
- Cash drawer tracking  
- Offline mode  
- Barcode scanning module  

### Business Intelligence
- Sales forecasts  
- Inventory turnover analytics  
- Accounting dashboards  

---

# 🏁 Summary

The ArcoírisPOS data model provides:

- Clean domain separation  
- Strong relational integrity  
- Scalable multi-tenant foundations  
- Accounting-grade ledger architecture  
- POS, Inventory, and Accounting interconnection  
- Future-proof structure for the Nano Business Suite  

This document serves as the authoritative reference for schema updates, migrations, and architectural decisions.

