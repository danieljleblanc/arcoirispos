#!/usr/bin/env python3
"""
ArcoirisPOS Development Seed Script
------------------------------------
Creates development demo data.
"""

import asyncio
import uuid
from sqlalchemy import text

from src.app.core.database import AsyncSessionLocal, engine
from src.app.core.base import Base

from src.app.org.models.organization_models import Organization
from src.app.org.models.organization_settings_model import OrganizationSettings
from src.app.org.models.user_models import User
from src.app.org.models.role_models import UserOrgRole, UserRole

from src.app.inventory.models.location_models import Location
from src.app.inventory.models.item_models import Item

from src.app.pos.models.customer_models import Customer
from src.app.pos.models.terminal_models import Terminal

from src.app.auth.services.hashing import hash_password


async def seed():
    print("\n=== Seeding Development Database ===\n")

    # ---------------------------------------------------------
    # Ensure schemas exist BEFORE metadata.create_all()
    # ---------------------------------------------------------
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS acct"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS inv"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS pos"))

        await conn.run_sync(Base.metadata.create_all)

    # ---------------------------------------------------------
    # Start DB session
    # ---------------------------------------------------------
    async with AsyncSessionLocal() as session:

        org_id = uuid.uuid4()
        admin_user_id = uuid.uuid4()

        # -----------------------------------------------------
        # 1. ORGANIZATION
        # -----------------------------------------------------
        org = Organization(
            org_id=org_id,
            name="Arcoiris POS",
            legal_name="Arcoiris POS LLC",
            display_name="Arcoiris POS",
            is_active=True,
        )
        session.add(org)

        # -----------------------------------------------------
        # 2. SETTINGS
        # -----------------------------------------------------
        settings_row = OrganizationSettings(
            settings_id=uuid.uuid4(),
            org_id=org_id,
            rounding_mode="none",
            rounding_apply_to="cash_only",
            inventory_mode="deduct_on_cart",
        )
        session.add(settings_row)

        # -----------------------------------------------------
        # 3. ADMIN USER
        # -----------------------------------------------------
        admin = User(
            user_id=admin_user_id,
            email="admin@arcoirispos.com",
            password_hash=hash_password("MyNewSecureAdmin123!"),
            display_name="Administrator",
            is_active=True,
        )
        session.add(admin)

        # -----------------------------------------------------
        # 4. ADMIN ROLE
        # -----------------------------------------------------
        admin_role = UserOrgRole(
            user_org_role_id=uuid.uuid4(),
            org_id=org_id,
            user_id=admin_user_id,
            role=UserRole.ADMIN.value,
            is_primary=True,
        )
        session.add(admin_role)

        # -----------------------------------------------------
        # 5. DEFAULT LOCATION
        # -----------------------------------------------------
        location = Location(
            location_id=uuid.uuid4(),
            org_id=org_id,
            name="Main Warehouse",
            code="MAIN-WH",
        )
        session.add(location)

        # -----------------------------------------------------
        # 6. DEFAULT ITEM
        # -----------------------------------------------------
        item = Item(
            item_id=uuid.uuid4(),
            org_id=org_id,
            sku="SKU-TEST-001",
            name="Test Item",
            description="Sample development item",
            item_type="product",
            default_price=9.99,
            cost_basis=5.00,
            is_active=True,
        )
        session.add(item)

        # -----------------------------------------------------
        # 7. DEFAULT CUSTOMER  (UPDATED MODEL)
        # -----------------------------------------------------
        customer = Customer(
            customer_id=uuid.uuid4(),
            org_id=org_id,
            first_name="Test",
            middle_name=None,
            last_name="Customer",
            email="customer@example.com",
            phone="555-123-4567",
            street_address="123 Main St",
            city="Springfield",
            state="CA",
            zip="90210",
        )
        session.add(customer)

        # -----------------------------------------------------
        # 8. TERMINAL
        # -----------------------------------------------------
        terminal = Terminal(
            terminal_id=uuid.uuid4(),
            org_id=org_id,
            name="Terminal 1",
            location_label="Main POS Terminal",
            is_active=True,
        )
        session.add(terminal)

        # -----------------------------------------------------
        # COMMIT EVERYTHING
        # -----------------------------------------------------
        await session.commit()

        print("\n✨ Seed complete! ✨\n")
        print("Login Credentials:")
        print("  Email:    admin@arcoirispos.com")
        print("  Password: MyNewSecureAdmin123!\n")


if __name__ == "__main__":
    asyncio.run(seed())
