--
-- ArcoírisPOS Migration 002 — Indexes
-- Optimized for: POS lookups, accounting joins, inventory performance,
-- multi-tenant SaaS queries, and foreign-key join efficiency.
--

------------------------------------------------------------
-- CORE INDEXES
------------------------------------------------------------

-- Organizations
CREATE INDEX idx_organizations_active
    ON core.organizations (is_active);

-- Users
CREATE INDEX idx_users_email
    ON core.users (email);

-- User roles
CREATE INDEX idx_user_org_roles_org
    ON core.user_org_roles (org_id);

CREATE INDEX idx_user_org_roles_user
    ON core.user_org_roles (user_id);


------------------------------------------------------------
-- POS INDEXES
------------------------------------------------------------

-- Terminals
CREATE INDEX idx_terminals_org
    ON pos.terminals (org_id);

-- Customers
CREATE INDEX idx_pos_customers_org
    ON pos.customers (org_id);

CREATE INDEX idx_pos_customers_email
    ON pos.customers (email);

CREATE INDEX idx_pos_customers_phone
    ON pos.customers (phone);

-- Tax rates
CREATE INDEX idx_tax_rates_org
    ON pos.tax_rates (org_id);


------------------------------------------------------------
-- INVENTORY INDEXES
------------------------------------------------------------

-- Items
CREATE INDEX idx_items_org
    ON inv.items (org_id);

CREATE INDEX idx_items_sku
    ON inv.items (sku);

CREATE INDEX idx_items_barcode
    ON inv.items (barcode);

-- Locations
CREATE INDEX idx_locations_org
    ON inv.locations (org_id);

-- Stock levels
CREATE INDEX idx_stock_levels_org_item_location
    ON inv.stock_levels (org_id, item_id, location_id);

-- Stock movements (heavy analytical table)
CREATE INDEX idx_stock_movements_org_item_date
    ON inv.stock_movements (org_id, item_id, occurred_at);

CREATE INDEX idx_stock_movements_source
    ON inv.stock_movements (source_type, source_id);


------------------------------------------------------------
-- POS SALES & PAYMENTS INDEXES
------------------------------------------------------------

-- Sales (this table will get heavy under load)
CREATE INDEX idx_sales_org
    ON pos.sales (org_id);

CREATE INDEX idx_sales_org_date
    ON pos.sales (org_id, sale_date);

CREATE INDEX idx_sales_customer
    ON pos.sales (customer_id);

CREATE INDEX idx_sales_terminal
    ON pos.sales (terminal_id);

CREATE INDEX idx_sales_status
    ON pos.sales (status);

-- Sale lines
CREATE INDEX idx_sale_lines_sale
    ON pos.sale_lines (sale_id);

CREATE INDEX idx_sale_lines_item
    ON pos.sale_lines (item_id);

-- Payments
CREATE INDEX idx_payments_sale
    ON pos.payments (sale_id);

CREATE INDEX idx_payments_method
    ON pos.payments (payment_method);

CREATE INDEX idx_payments_org_date
    ON pos.payments (org_id, processed_at);


------------------------------------------------------------
-- ACCOUNTING INDEXES
------------------------------------------------------------

-- Chart of accounts
CREATE INDEX idx_chart_of_accounts_org
    ON acct.chart_of_accounts (org_id);

CREATE INDEX idx_chart_of_accounts_type
    ON acct.chart_of_accounts (type);

-- Journal entries
CREATE INDEX idx_journal_entries_org_date
    ON acct.journal_entries (org_id, journal_date);

CREATE INDEX idx_journal_entries_source
    ON acct.journal_entries (source_type, source_id);

CREATE INDEX idx_journal_entries_posted
    ON acct.journal_entries (posted);

-- Journal lines
CREATE INDEX idx_journal_lines_journal
    ON acct.journal_lines (journal_id);

CREATE INDEX idx_journal_lines_account
    ON acct.journal_lines (account_id);

CREATE INDEX idx_journal_lines_org
    ON acct.journal_lines (org_id);

-- Customer balances (AR helper)
CREATE INDEX idx_customer_balances_org_customer
    ON acct.customer_balances (org_id, customer_id);

-- Bank accounts
CREATE INDEX idx_bank_accounts_org
    ON acct.bank_accounts (org_id);
