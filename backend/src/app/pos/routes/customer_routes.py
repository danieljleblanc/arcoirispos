# backend/src/app/pos/routes/customer_routes.py

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
from src.app.pos.services.customer_service import customer_service
from src.app.pos.schemas.pos_schemas import (
    CustomerCreate,
    CustomerRead,
)

router = APIRouter(prefix="/customers", tags=["customers"])


# ---------------------------------------------------------
# CREATE CUSTOMER (any staff)
# ---------------------------------------------------------
@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    data = payload.dict()
    data["org_id"] = org_id

    customer = await customer_service.create(session, data)
    await session.commit()
    return customer


# ---------------------------------------------------------
# LIST CUSTOMERS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[CustomerRead])
async def list_customers(
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    return await customer_service.get_by_org(session, org_id)


# ---------------------------------------------------------
# GET CUSTOMER (any staff)
# ---------------------------------------------------------
@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    customer = await customer_service.get_by_id(session, customer_id)

    if not customer or customer.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


# ---------------------------------------------------------
# DELETE CUSTOMER (admin only — soft delete)
# ---------------------------------------------------------
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    customer = await customer_service.get_by_id(session, customer_id)
    if not customer or customer.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    deleted = await customer_service.delete_customer(session, customer_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete customer",
        )

    await session.commit()
    return None
