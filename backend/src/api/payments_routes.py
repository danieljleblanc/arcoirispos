from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.pos_schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentUpdate,
)
from src.services.pos.payments import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


# ---- LIST BY ORG ----
@router.get("/", response_model=List[PaymentRead])
async def list_payments(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await payment_service.get_by_org(session, org_id, limit, offset)


# ---- LIST BY SALE ----
@router.get("/sale/{sale_id}", response_model=List[PaymentRead])
async def list_payments_for_sale(
    sale_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await payment_service.get_by_sale(session, sale_id)


# ---- GET SINGLE PAYMENT ----
@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    payment = await payment_service.get_by_id(session, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return payment


# ---- CREATE ----
@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_session),
):
    payment = await payment_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(payment)
    return payment


# ---- UPDATE ----
@router.patch("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: UUID,
    payload: PaymentUpdate,
    session: AsyncSession = Depends(get_session),
):
    payment = await payment_service.get_by_id(session, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(payment, field, value)

    await session.commit()
    await session.refresh(payment)
    return payment


# ---- DELETE ----
@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await payment_service.delete(session, payment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    await session.commit()
