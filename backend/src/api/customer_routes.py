# backend/src/api/customer_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import (
    require_any_staff,
    require_admin,
)

from src.services.pos.customers import customer_service
from src.schemas.pos_schemas import (
    CustomerCreate,
    CustomerRead,
)

router = APIRouter(prefix="/customers", tags=["customers"])


# ---------------------------------------------------------
# CREATE CUSTOMER  (any staff allowed)
# ---------------------------------------------------------
@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_any_staff),
):
    customer = await customer_service.create(session, payload.dict())
    await session.commit()
    return customer


# ---------------------------------------------------------
# LIST CUSTOMERS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[CustomerRead])
async def list_customers(
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_any_staff),
):
    return await customer_service.get_by_org(session, org_id)


# ---------------------------------------------------------
# GET CUSTOMER (any staff)
# ---------------------------------------------------------
@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_any_staff),
):
    customer = await customer_service.get_by_id(session, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# ---------------------------------------------------------
# DELETE CUSTOMER (admin only) – SOFT DELETE
# ---------------------------------------------------------
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_admin),
):
    deleted = await customer_service.delete_customer(session, customer_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")

    await session.commit()
    return None
