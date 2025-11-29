## ✅ (1) INVENTORY MODEL EXTENSION PROPOSAL
Technical Specification — Inventory Reservation Layer

Below is the recommended approach for implementing a unified inventory reservation system that supports:

POS in-store carts

Suspended orders

Online order imports (Amazon/Etsy/Shopify/etc.)

Multi-cashier / single-terminal queue

Pre-orders

Backorders

Partial-ship workflows

A. Core Concepts

Every item must have three independent quantities:

Field	Meaning	Changes When
qty_on_hand	Physical stock in store / warehouse	Receiving, returns, adjustments, completed sale
qty_reserved	Stock promised but not yet sold	Adding to cart, suspending, online open orders
qty_available	Sellable stock right now	Derived: qty_on_hand - qty_reserved

qty_available must never be stored — it is always computed.

B. Required Data Model Changes
## 1. Extend StockLevel table

You already have StockLevel in the inventory module; we extend it:

qty_on_hand: Mapped[Numeric]
qty_reserved: Mapped[Numeric]


Nothing else changes in the core structure.

## 2. Introduce InventoryReservation table (recommended)

This is the flexible, future-proof design.

class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    __table_args__ = {"schema": "inv"}

    reservation_id: UUID (PK)
    org_id: UUID
    location_id: UUID
    item_id: UUID
    sale_line_id: UUID (nullable until line is created)
    quantity: Numeric
    status: Enum("active", "released", "consumed")
    created_at
    updated_at


Why this matters:

Every open order (POS or online) creates reservations

Suspension keeps reservations active

Cancellation releases reservations

Completion consumes and reduces qty_on_hand

This is how major systems like Lightspeed, Clover, Shopify POS, Square, Toast behave internally.

C. Reservation Flow Logic
1. Add Item to Cart

Create or update a reservation:

qty_reserved += n

Automatically recomputes:

qty_available = qty_on_hand - qty_reserved

2. Edit Cart

Increase quantity → increase reservation

Decrease quantity → decrease reservation

3. Suspend Order

Reservation remains

Order enters the global work queue

Any cashier may resume

4. Resume Order

No reservation changes unless item qty changes

5. Complete Sale

For each reservation:

qty_on_hand -= quantity

qty_reserved -= quantity

Post COGS and inventory asset adjustments to accounting

Mark reservations → consumed

6. Cancel/Discard Order

For each reservation:

qty_reserved -= quantity

Mark reservations → released

7. Online Order Imports

When importing from:

Amazon

Etsy

Shopify

Website

Immediately create reservations

Order becomes a POS Suspended Sale, ready for fulfillment

This prevents overselling across channels — the #1 issue that kills small retailers using cheap POS systems.

## ✅ (2) PROJECT DOCUMENT — INVENTORY RESERVATION SYSTEM
Place this file in the repo:

docs/specs/InventoryReservationSpec_YYYY-MM-DD.md
(Using your PascalCase naming convention)

Below is the complete Markdown document — fully formatted and ready to paste.

Inventory Reservation System — Functional & Technical Specification

Arco Iris POS — Core Architecture
Version: Draft
Date: 2025-11-27

1. Purpose

This document defines the behavior, data model, and lifecycle rules for the Inventory Reservation System, a core component of the Arco Iris POS inventory architecture.

This system enables:

Multi-cashier use of a single terminal

Accurate stock levels during open/suspended orders

Prevention of overselling across online and in-store channels

Future integration with Amazon, Etsy, Shopify, WooCommerce

Support for pre-orders, backorders, and partial fulfillment

This feature differentiates Arco Iris POS as a serious multi-channel retail platform, not merely a point-of-sale register.

2. Key Definitions
Qty On Hand

Physical inventory currently owned by the store.

Qty Reserved

Inventory allocated to open or suspended orders but not yet sold.

Qty Available
qty_available = qty_on_hand - qty_reserved


This is always computed dynamically.

3. Data Model Requirements
3.1 StockLevel Enhancements

Add:

qty_on_hand     # physical stock
qty_reserved    # reserved but not sold

3.2 InventoryReservation Table

A flexible record of item allocations across sales channels.

Fields:

reservation_id

org_id

location_id

item_id

sale_line_id (nullable until created)

quantity

status:

active

released

consumed

timestamps

4. Lifecycle Behavior
4.1 Add to Cart

Increase reservation

Decrease availability

4.2 Edit Cart

Adjust reservations accordingly

4.3 Suspend Order

Keep reservations active

Order moves to the shared cashier queue

4.4 Resume Order

No change

4.5 Complete Sale

Convert reservation to permanent inventory movement

Reduce qty_on_hand

Reduce qty_reserved

Post accounting entries (COGS, asset reduction, revenue)

4.6 Cancel / Void

Release reservations

Do not reduce qty_on_hand

Do not post accounting entries

4.7 Online Orders

Upon import:

Create reservation

Create suspended sale

Prevent overselling across all channels

5. Accounting Implications

Reservations are operational, not financial.

Only completed sales generate:

COGS

Inventory Asset reductions

Revenue & tax

Journal entries

This separation follows GAAP/IFRS principles and avoids premature revenue recognition.

6. Future Extensions

The system supports:

Pre-orders

Backorders

Partial fulfillment / multi-shipment

Warehouse transfers

Multi-location inventory

Vendor dropship workflows

No redesign is needed later — this foundation scales.

7. Summary

This reservation framework ensures Arco Iris POS:

Competes with enterprise systems

Avoids overselling

Supports multi-cashier queues

Enables multi-channel retail

Remains GAAP-compliant

Is ready for future expansion without refactoring

This is a core architecture element, not an optional enhancement.