--
-- ArcoírisPOS Phase 1–3 PostgreSQL Schema
-- Author: Daniel LeBlanc / Foreside Holdings
-- Lowercase + snake_case — PostgreSQL-safe
--

------------------------------------------------------------
-- EXTENSIONS
------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "citext";    -- for case-insensitive emails


------------------------------------------------------------
-- ENUMS
------------------------------------------------------------

CREATE TYPE acct_entry_type AS ENUM ('debit', 'credit');


------------------------------------------------------------
-- SCHEMAS
------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS pos;
CREATE SCHEMA IF NOT EXISTS inv;
CREATE SCHEMA IF NOT EXISTS acct;


------------------------------------------------------------
-- CORE SCHEMA
------------------------------------------------------------

--
-- Organizations (tenants)
--

CREATE TABLE core.organizations (
    org_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    legal_name      TEXT,
    timezone        TEXT NOT NULL DEFAULT 'UTC',
    base_currency   TEXT NOT NULL DEFAULT 'USD',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);


--
-- Users
--

CREATE TABLE core.users (
    user_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           CITEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    display_name    TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


--
-- User → Organization Role Membership
--

CREATE TABLE core.user_org_roles (
    user_org_role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    user_id         UUID NOT NULL REFERENCES core.users(user_id),
    role            TEXT NOT NULL,  -- 'owner','manager','cashier','accountant'
    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, user_id, role)
);


------------------------------------------------------------
-- POS SCHEMA
------------------------------------------------------------

--
-- POS Terminals
--

CREATE TABLE pos.terminals (
    terminal_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    name            TEXT NOT NULL,
    location_label  TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


--
-- POS Customers
--

CREATE TABLE pos.customers (
    customer_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    external_ref    TEXT,
    full_name       TEXT NOT NULL,
    email           CITEXT,
    phone           TEXT,
    billing_address JSONB,
    shipping_address JSONB,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);


--
-- Tax Rates
--

CREATE TABLE pos.tax_rates (
    tax_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    name            TEXT NOT NULL,
    rate_percent    NUMERIC(9,4) NOT NULL,
    is_compound     BOOLEAN NOT NULL DEFAULT FALSE,
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


------------------------------------------------------------
-- INVENTORY SCHEMA
------------------------------------------------------------

--
-- Items (Products / Services)
--

CREATE TABLE inv.items (
    item_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    sku             TEXT,
    barcode         TEXT,
    name            TEXT NOT NULL,
    description     TEXT,
    item_type       TEXT NOT NULL,         -- 'product','service','fee'
    default_price   NUMERIC(18,4) NOT NULL DEFAULT 0,
    cost_basis      NUMERIC(18,4),
    tax_id          UUID REFERENCES pos.tax_rates(tax_id),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);


--
-- Inventory Locations
--

CREATE TABLE inv.locations (
    location_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    name            TEXT NOT NULL,
    code            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);


--
-- Stock Levels (computed or cached)
--

CREATE TABLE inv.stock_levels (
    stock_level_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID NOT NULL REFERENCES core.organizations(org_id),
    item_id             UUID NOT NULL REFERENCES inv.items(item_id),
    location_id         UUID NOT NULL REFERENCES inv.locations(location_id),
    quantity_on_hand    NUMERIC(18,4) NOT NULL DEFAULT 0,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, item_id, location_id)
);


--
-- Stock Movements (immutable audit for inventory)
--

CREATE TABLE inv.stock_movements (
    movement_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    item_id         UUID NOT NULL REFERENCES inv.items(item_id),
    location_id     UUID NOT NULL REFERENCES inv.locations(location_id),
    source_type     TEXT NOT NULL,        -- 'sale','purchase','adjustment'
    source_id       UUID,
    quantity_delta  NUMERIC(18,4) NOT NULL,
    unit_cost       NUMERIC(18,4),
    occurred_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


------------------------------------------------------------
-- POS SALES & PAYMENTS
------------------------------------------------------------

--
-- Sales (POS Transactions)
--

CREATE TABLE pos.sales (
    sale_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    terminal_id     UUID REFERENCES pos.terminals(terminal_id),
    customer_id     UUID REFERENCES pos.customers(customer_id),
    sale_number     TEXT,
    status          TEXT NOT NULL,              -- 'open','completed','void','refunded'
    sale_type       TEXT NOT NULL DEFAULT 'pos',
    subtotal        NUMERIC(18,4) NOT NULL DEFAULT 0,
    tax_total       NUMERIC(18,4) NOT NULL DEFAULT 0,
    discount_total  NUMERIC(18,4) NOT NULL DEFAULT 0,
    grand_total     NUMERIC(18,4) NOT NULL DEFAULT 0,
    amount_paid     NUMERIC(18,4) NOT NULL DEFAULT 0,
    balance_due     NUMERIC(18,4) NOT NULL DEFAULT 0,
    sale_date       TIMESTAMPTZ NOT NULL,
    notes           TEXT,
    created_by      UUID REFERENCES core.users(user_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);


--
-- Sale Line Items
--

CREATE TABLE pos.sale_lines (
    sale_line_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    sale_id         UUID NOT NULL REFERENCES pos.sales(sale_id) ON DELETE CASCADE,
    line_number     INT NOT NULL,
    item_id         UUID NOT NULL REFERENCES inv.items(item_id),
    description     TEXT,
    quantity        NUMERIC(18,4) NOT NULL,
    unit_price      NUMERIC(18,4) NOT NULL,
    discount_amount NUMERIC(18,4) NOT NULL DEFAULT 0,
    tax_id          UUID REFERENCES pos.tax_rates(tax_id),
    tax_amount      NUMERIC(18,4) NOT NULL DEFAULT 0,
    line_total      NUMERIC(18,4) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sale_id, line_number)
);


--
-- Payments (Cash / Card / Mixed)
--

CREATE TABLE pos.payments (
    payment_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    sale_id         UUID NOT NULL REFERENCES pos.sales(sale_id) ON DELETE CASCADE,
    payment_method  TEXT NOT NULL,        -- 'cash','card','online'
    amount          NUMERIC(18,4) NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'USD',
    external_ref    TEXT,                 -- PSP transaction id
    processed_at    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


------------------------------------------------------------
-- ACCOUNTING SCHEMA (DOUBLE ENTRY)
------------------------------------------------------------

--
-- Chart of Accounts
--

CREATE TABLE acct.chart_of_accounts (
    account_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    code            TEXT NOT NULL,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,        -- 'asset','liability','equity','revenue','expense'
    subtype         TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    parent_id       UUID REFERENCES acct.chart_of_accounts(account_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, code)
);


--
-- Journal Entries (headers)
--

CREATE TABLE acct.journal_entries (
    journal_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    journal_number  TEXT,
    source_type     TEXT,
    source_id       UUID,
    description     TEXT,
    journal_date    DATE NOT NULL,
    posted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_by      UUID REFERENCES core.users(user_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


--
-- Journal Lines (debits/credits)
--

CREATE TABLE acct.journal_lines (
    journal_line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_id      UUID NOT NULL REFERENCES acct.journal_entries(journal_id) ON DELETE CASCADE,
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    line_number     INT NOT NULL,
    account_id      UUID NOT NULL REFERENCES acct.chart_of_accounts(account_id),
    entry_type      acct_entry_type NOT NULL,
    amount          NUMERIC(18,4) NOT NULL CHECK (amount > 0),
    memo            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (journal_id, line_number)
);


--
-- Customer AR Balances (optional optimization)
--

CREATE TABLE acct.customer_balances (
    customer_balance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    customer_id     UUID NOT NULL REFERENCES pos.customers(customer_id),
    account_id      UUID NOT NULL REFERENCES acct.chart_of_accounts(account_id),
    balance         NUMERIC(18,4) NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, customer_id, account_id)
);


--
-- Bank Accounts linked to Chart of Accounts
--

CREATE TABLE acct.bank_accounts (
    bank_account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES core.organizations(org_id),
    account_id      UUID NOT NULL REFERENCES acct.chart_of_accounts(account_id),
    display_name    TEXT NOT NULL,
    institution     TEXT,
    last4           TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (org_id, account_id)
);
