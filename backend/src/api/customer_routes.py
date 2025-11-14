from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.core.database import get_session
from src.models.customer import Customer
from src.schemas.customer_schemas import CustomerCreate, CustomerOut

router = APIRouter(prefix="/customers", tags=["Customers"])


# ─────────────────────────────────────────────
# CREATE CUSTOMER
# ─────────────────────────────────────────────
@router.post("/", response_model=CustomerOut)
async def create_customer(
    payload: CustomerCreate,
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    new_customer = Customer(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        organization_id=organization_id
    )

    session.add(new_customer)
    await session.commit()
    await session.refresh(new_customer)
    return new_customer


# ─────────────────────────────────────────────
# GET CUSTOMER BY ID
# ─────────────────────────────────────────────
@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
):
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# ─────────────────────────────────────────────
# LIST CUSTOMERS
# ─────────────────────────────────────────────
@router.get("/", response_model=list[CustomerOut])
async def list_customers(
    organization_id: int = 1,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Customer)
        .where(Customer.organization_id == organization_id)
        .order_by(Customer.last_name.asc(), Customer.first_name.asc())
        .limit(limit)
    )
    return result.scalars().all()


# ─────────────────────────────────────────────
# UPDATE CUSTOMER
# ─────────────────────────────────────────────
@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: int,
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        update(Customer)
        .where(Customer.id == customer_id)
        .values(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone
        )
        .returning(Customer)
    )

    updated = result.fetchone()
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")

    await session.commit()
    return updated[0]


# ─────────────────────────────────────────────
# DELETE CUSTOMER
# ─────────────────────────────────────────────
@router.delete("/{customer_id}", response_model=dict)
async def delete_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        delete(Customer).where(Customer.id == customer_id).returning(Customer.id)
    )
    deleted = result.scalar()

    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")

    await session.commit()
    return {"status": "deleted", "customer_id": customer_id}
