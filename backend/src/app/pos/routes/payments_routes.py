# backend/src/app/pos/routes/payments_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_session

# ---------------------------------------------------------
# Correct security imports
# ---------------------------------------------------------
from src.app.auth.services.org_context import get_current_org
from src.app.auth.services.dependencies import (
    require_any_staff_org,
    require_admin_org,
)

# ---------------------------------------------------------
# Correct service + schema imports
# ---------------------------------------------------------
from src.app.pos.services.payment_service import payment_service
from src.app.pos.schemas.pos_schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentUpdate,
)

router = APIRouter(prefix="/payments", tags=["payments"])


# ---------------------------------------------------------
# LIST PAYMENTS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[PaymentRead])
async def list_payments(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    return await payment_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# LIST PAYMENTS FOR A SALE (any staff)
# ---------------------------------------------------------
@router.get("/sale/{sale_id}", response_model=List[PaymentRead])
async def list_payments_for_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    # The service will handle org validation if required later
    return await payment_service.get_by_sale(session, sale_id)


# ---------------------------------------------------------
# GET PAYMENT (any staff)
# ---------------------------------------------------------
@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    payment = await payment_service.get_by_id(session, payment_id)

    if not payment or payment.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


# ---------------------------------------------------------
# CREATE PAYMENT (admin / manager / owner)
# ---------------------------------------------------------
@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    data = payload.dict()
    data["org_id"] = org_id

    payment = await payment_service.create(session, data)
    await session.commit()
    await session.refresh(payment)
    return payment


# ---------------------------------------------------------
# UPDATE PAYMENT (admin / manager / owner)
# ---------------------------------------------------------
@router.patch("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: UUID,
    payload: PaymentUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    payment = await payment_service.get_by_id(session, payment_id)
    if not payment or payment.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(payment, field, value)

    await session.commit()
    await session.refresh(payment)
    return payment


# ---------------------------------------------------------
# DELETE PAYMENT (admin / manager / owner)
# ---------------------------------------------------------
@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    payment = await payment_service.get_by_id(session, payment_id)
    if not payment or payment.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    deleted = await payment_service.delete_payment(session, payment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete payment",
        )

    await session.commit()
    return None
