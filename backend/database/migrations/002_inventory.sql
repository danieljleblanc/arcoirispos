-- ===========================================================
-- 002_inventory.sql
-- Phase 2 Inventory Tables and Item Extensions
-- ===========================================================

-- -----------------------------------------------------------
-- 1. Vendors
-- -----------------------------------------------------------
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vendors_org ON vendors (organization_id);


-- -----------------------------------------------------------
-- 2. Extend items table for inventory support
-- -----------------------------------------------------------
ALTER TABLE items
    ADD COLUMN vendor_id INT NULL,
    ADD COLUMN cost NUMERIC(10,2) NULL,
    ADD COLUMN track_stock BOOLEAN DEFAULT TRUE,
    ADD COLUMN reorder_point INT NULL;

ALTER TABLE items
    ADD CONSTRAINT fk_items_vendor
        FOREIGN KEY (vendor_id) REFERENCES vendors (id);


-- -----------------------------------------------------------
-- 3. Stock Levels (per location)
-- -----------------------------------------------------------
CREATE TABLE stock_levels (
    id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES items (id),
    location_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stock_levels_item ON stock_levels (item_id);
CREATE INDEX idx_stock_levels_location ON stock_levels (location_id);


-- -----------------------------------------------------------
-- 4. Inventory Transactions (audit log)
-- -----------------------------------------------------------
CREATE TABLE inventory_transactions (
    id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES items (id),
    location_id INT NOT NULL,
    quantity_change INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    reference_id INT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inv_tx_item ON inventory_transactions (item_id);
CREATE INDEX idx_inv_tx_location ON inventory_transactions (location_id);
CREATE INDEX idx_inv_tx_type ON inventory_transactions (transaction_type);


-- -----------------------------------------------------------
-- 5. Purchase Orders
-- -----------------------------------------------------------
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    vendor_id INT NOT NULL REFERENCES vendors (id),
    organization_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    received_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_po_vendor ON purchase_orders (vendor_id);
CREATE INDEX idx_po_org ON purchase_orders (organization_id);


-- -----------------------------------------------------------
-- 6. Purchase Order Lines
-- -----------------------------------------------------------
CREATE TABLE purchase_order_lines (
    id SERIAL PRIMARY KEY,
    po_id INT NOT NULL REFERENCES purchase_orders (id),
    item_id INT NOT NULL REFERENCES items (id),
    quantity INT NOT NULL,
    cost NUMERIC(10,2) NOT NULL
);

CREATE INDEX idx_po_lines_po ON purchase_order_lines (po_id);
CREATE INDEX idx_po_lines_item ON purchase_order_lines (item_id);


-- ===========================================================
-- END OF 002_inventory.sql
-- ===========================================================
