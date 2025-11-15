from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from src.models.sale import Sale, SaleLine
from src.models.payment import Payment
from src.models.item import Item


# ─────────────────────────────────────────────
# CREATE SALE
# ─────────────────────────────────────────────
async def create_sale(session: AsyncSession, customer_id: int | None, organization_id: int):
    new_sale = Sale(
        customer_id=customer_id,
        organization_id=organization_id,
        total_amount=0
    )
    session.add(new_sale)
    await session.flush()  # ensures sale.id is populated
    return new_sale


# ─────────────────────────────────────────────
# ADD SALE LINE
# ─────────────────────────────────────────────
async def add_sale_line(session: AsyncSession, sale_id: int, item_id: int, quantity: int):
    # Fetch item to get price
    item = await session.get(Item, item_id)
    if not item:
        raise ValueError(f"Item {item_id} not found")

    line_total = item.price * quantity

    sale_line = SaleLine(
        sale_id=sale_id,
        item_id=item_id,
        quantity=quantity,
        line_total=line_total
    )

    session.add(sale_line)

    # Update sale.amount
    await update_sale_total(session, sale_id)

    await session.flush()
    return sale_line


# ─────────────────────────────────────────────
# UPDATE SALE TOTAL (Recalculates)
# ─────────────────────────────────────────────
async def update_sale_total(session: AsyncSession, sale_id: int):
    result = await session.execute(
        select(func.sum(SaleLine.line_total)).where(SaleLine.sale_id == sale_id)
    )
    total = result.scalar() or 0

    await session.execute(
        update(Sale).where(Sale.id == sale_id).values(total_amount=total)
    )

    await session.flush()
    return total


# ─────────────────────────────────────────────
# RECORD PAYMENT
# ─────────────────────────────────────────────
async def record_payment(session: AsyncSession, sale_id: int, method: str, amount: float):
    payment = Payment(
        sale_id=sale_id,
        method=method,
        amount=amount,
    )
    session.add(payment)
    await session.flush()
    return payment


# ─────────────────────────────────────────────
# GET SALE WITH LINES & PAYMENTS
# ─────────────────────────────────────────────
async def get_sale(session: AsyncSession, sale_id: int):
    result = await session.execute(
        select(Sale)
        .where(Sale.id == sale_id)
        .options(
            Sale.lines,
            Sale.payments,
            Sale.customer
        )
    )
    return result.scalar_one_or_none()


# ─────────────────────────────────────────────
# LIST SALES BY ORGANIZATION (Common Use Case)
# ─────────────────────────────────────────────
async def list_sales(session: AsyncSession, organization_id: int, limit=50):
    result = await session.execute(
        select(Sale)
        .where(Sale.organization_id == organization_id)
        .order_by(Sale.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


# ─────────────────────────────────────────────
# DELETE SALE (Optional: Soft Delete)
# ─────────────────────────────────────────────
async def delete_sale(session: AsyncSession, sale_id: int):
    await session.execute(delete(Sale).where(Sale.id == sale_id))
    await session.flush()
    return True
