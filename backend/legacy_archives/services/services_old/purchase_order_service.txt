from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models.purchase_order import PurchaseOrder
from src.models.purchase_order_line import PurchaseOrderLine
from src.models.vendor import Vendor
from src.services.stock_service import adjust_stock


# ─────────────────────────────────────────────
# CREATE PURCHASE ORDER
# ─────────────────────────────────────────────
async def create_purchase_order(session: AsyncSession, organization_id: int,
                                vendor_id: int, lines: list):

    # Ensure vendor exists
    vendor = await session.get(Vendor, vendor_id)
    if not vendor:
        raise ValueError("Vendor does not exist")

    po = PurchaseOrder(
        vendor_id=vendor_id,
        organization_id=organization_id,
        status="open"
    )
    session.add(po)
    await session.flush()   # get PO ID

    # Insert PO lines
    for line in lines:
        po_line = PurchaseOrderLine(
            po_id=po.id,
            item_id=line.item_id,
            quantity=line.quantity,
            cost=line.cost
        )
        session.add(po_line)

    await session.commit()
    await session.refresh(po)
    return po


# ─────────────────────────────────────────────
# RECEIVE PURCHASE ORDER (atomic inventory update)
# ─────────────────────────────────────────────
async def receive_purchase_order(session: AsyncSession, po_id: int, location_id: int):

    po = await session.get(PurchaseOrder, po_id)
    if not po:
        raise ValueError("Purchase order not found")

    # Load lines
    result = await session.execute(
        select(PurchaseOrderLine).where(PurchaseOrderLine.po_id == po_id)
    )
    lines = result.scalars().all()

    # Add stock for each line
    for line in lines:
        await adjust_stock(
            session=session,
            item_id=line.item_id,
            location_id=location_id,
            quantity_change=line.quantity,
            transaction_type="purchase_order",
            reference_id=po_id
        )

    # Mark PO received
    await session.execute(
        update(PurchaseOrder)
        .where(PurchaseOrder.id == po_id)
        .values(status="received")
    )

    await session.commit()
    return True


# ─────────────────────────────────────────────
# GET PO
# ─────────────────────────────────────────────
async def get_purchase_order(session: AsyncSession, po_id: int):
    return await session.get(PurchaseOrder, po_id)


# ─────────────────────────────────────────────
# LIST POs
# ─────────────────────────────────────────────
async def list_purchase_orders(session: AsyncSession, organization_id: int):
    result = await session.execute(
        select(PurchaseOrder)
        .where(PurchaseOrder.organization_id == organization_id)
        .order_by(PurchaseOrder.created_at.desc())
    )
    return result.scalars().all()
