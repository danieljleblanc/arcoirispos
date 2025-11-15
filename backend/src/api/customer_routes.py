from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.services.pos.customers import customer_service
from src.schemas.pos_schemas import (
    CustomerCreate,
    CustomerRead,
)

router = APIRouter(prefix="/pos/customers", tags=["Customers"])


@router.post("/", response_model=CustomerRead)
async def create_customer(
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_session),
):
    customer = await customer_service.create(session, payload.dict())
    await session.commit()
    return customer


@router.get("/", response_model=List[CustomerRead])
async def list_customers(
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    customers = await customer_service.get_by_org(session, org_id)
    return customers


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    customer = await customer_service.get_by_id(session, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# ⭐ NEW DELETE ENDPOINT — SOFT DELETE
@router.delete("/{customer_id}", response_model=CustomerRead)
async def delete_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    customer = await customer_service.delete_customer(session, customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    await session.commit()
    return customer
