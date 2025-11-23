from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.org_context import get_current_org
from src.core.security.dependencies import (
    require_any_staff_org,
    require_admin_org,
)
from src.services.pos.customers import customer_service
from src.schemas.pos_schemas import (
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
    """
    Create a customer *for the current organization*.
    The org_id comes from the X-Org-ID header via get_current_org().
    """

    customer_data = payload.dict()
    customer_data["org_id"] = org_ctx["org"].org_id

    customer = await customer_service.create(session, customer_data)
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
    """
    Return all customers for the active organization.
    """
    return await customer_service.get_by_org(session, org_ctx["org"].org_id)


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
    """
    Get a single customer by id, ensuring it belongs to the active org.
    """

    customer = await customer_service.get_by_id(session, customer_id)

    if not customer or customer.org_id != org_ctx["org"].org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    return customer


# ---------------------------------------------------------
# DELETE CUSTOMER (admin only) – SOFT DELETE
# ---------------------------------------------------------
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    """
    Soft-delete a customer IF they belong to the current organization AND
    the user has an admin-level role.
    """

    customer = await customer_service.get_by_id(session, customer_id)
    if not customer or customer.org_id != org_ctx["org"].org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    deleted = await customer_service.delete_customer(session, customer_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    await session.commit()
    return None
