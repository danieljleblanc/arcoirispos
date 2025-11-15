from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.vendor_schemas import VendorCreate, VendorOut
from src.services.vendor_service import (
    create_vendor, get_vendor, list_vendors, update_vendor, delete_vendor
)

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorOut)
async def create_vendor_endpoint(
    payload: VendorCreate,
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    vendor = await create_vendor(
        session=session,
        organization_id=organization_id,
        name=payload.name,
        contact_name=payload.contact_name,
        email=payload.email,
        phone=payload.phone
    )
    return vendor


@router.get("/", response_model=list[VendorOut])
async def list_vendors_endpoint(
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    return await list_vendors(session, organization_id)


@router.get("/{vendor_id}", response_model=VendorOut)
async def get_vendor_endpoint(
    vendor_id: int,
    session: AsyncSession = Depends(get_session),
):
    vendor = await get_vendor(session, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/{vendor_id}", response_model=VendorOut)
async def update_vendor_endpoint(
    vendor_id: int,
    payload: VendorCreate,
    session: AsyncSession = Depends(get_session),
):
    vendor = await update_vendor(session, vendor_id, **payload.model_dump())
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.delete("/{vendor_id}", response_model=dict)
async def delete_vendor_endpoint(
    vendor_id: int,
    session: AsyncSession = Depends(get_session),
):
    await delete_vendor(session, vendor_id)
    return {"status": "deleted", "vendor_id": vendor_id}
