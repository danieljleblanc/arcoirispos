from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.sale_schemas import (
    SaleCreate,
    SaleOut,
    SaleLineCreate,
    SaleLineOut,
    PaymentCreate,
    PaymentOut
)
from src.schemas.checkout_schemas import CheckoutRequest

from src.services.sales_service import (
    create_sale,
    add_sale_line,
    update_sale_total,
    record_payment,
    get_sale,
    list_sales,
    delete_sale
)

router = APIRouter(prefix="/sales", tags=["Sales"])


# ─────────────────────────────────────────────
# CREATE SALE
# ─────────────────────────────────────────────
@router.post("/", response_model=SaleOut)
async def create_sale_endpoint(
    payload: SaleCreate,
    organization_id: int = 1,  # placeholder multi-tenant support
    session: AsyncSession = Depends(get_session),
):
    sale = await create_sale(
        session=session,
        customer_id=payload.customer_id,
        organization_id=organization_id
    )

    # If sale lines were sent in request → add them now
    for line in payload.lines or []:
        await add_sale_line(
            session=session,
            sale_id=sale.id,
            item_id=line.item_id,
            quantity=line.quantity
        )

    await session.commit()

    full_sale = await get_sale(session, sale.id)
    return full_sale


# ─────────────────────────────────────────────
# ADD A SALE LINE
# ─────────────────────────────────────────────
@router.post("/{sale_id}/lines", response_model=SaleLineOut)
async def add_sale_line_endpoint(
    sale_id: int,
    payload: SaleLineCreate,
    session: AsyncSession = Depends(get_session),
):
    line = await add_sale_line(
        session=session,
        sale_id=sale_id,
        item_id=payload.item_id,
        quantity=payload.quantity
    )

    await session.commit()
    return line


# ─────────────────────────────────────────────
# RECORD PAYMENT
# ─────────────────────────────────────────────
@router.post("/{sale_id}/payments", response_model=PaymentOut)
async def record_payment_endpoint(
    sale_id: int,
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_session),
):
    payment = await record_payment(
        session=session,
        sale_id=sale_id,
        method=payload.method,
        amount=payload.amount
    )

    # Update sale total in case of adjustments
    await update_sale_total(session, sale_id)

    await session.commit()
    return payment


# ─────────────────────────────────────────────
# GET SALE WITH LINES + PAYMENTS
# ─────────────────────────────────────────────
@router.get("/{sale_id}", response_model=SaleOut)
async def get_sale_endpoint(
    sale_id: int,
    session: AsyncSession = Depends(get_session),
):
    sale = await get_sale(session, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


# ─────────────────────────────────────────────
# LIST SALES FOR ORGANIZATION
# ─────────────────────────────────────────────
@router.get("/", response_model=list[SaleOut])
async def list_sales_endpoint(
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    sales = await list_sales(session, organization_id)
    return sales


# ─────────────────────────────────────────────
# DELETE SALE
# ─────────────────────────────────────────────
@router.delete("/{sale_id}", response_model=dict)
async def delete_sale_endpoint(
    sale_id: int,
    session: AsyncSession = Depends(get_session),
):
    await delete_sale(session, sale_id)
    await session.commit()

    return {"status": "deleted", "sale_id": sale_id}

@router.post("/checkout", response_model=SaleOut)
async def full_sale_checkout(
    request: CheckoutRequest,
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    sale_data = request.sale
    payment_data = request.payment

    try:
        # 1. Create sale
        sale = await create_sale(
            session=session,
            customer_id=sale_data.customer_id,
            organization_id=organization_id
        )

        # 2. Add line items
        for line in sale_data.lines or []:
            await add_sale_line(
                session=session,
                sale_id=sale.id,
                item_id=line.item_id,
                quantity=line.quantity
            )

        # 3. Update total
        await update_sale_total(session, sale.id)

        # 4. Record payment
        await record_payment(
            session=session,
            sale_id=sale.id,
            method=payment_data.method,
            amount=payment_data.amount
        )

        await session.commit()
        return await get_sale(session, sale.id)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Checkout failed: {str(e)}")
