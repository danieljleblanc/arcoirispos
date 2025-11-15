from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.purchase_order_schemas import PurchaseOrderCreate, PurchaseOrderOut
from src.services.purchase_order_service import (
    create_purchase_order,
    receive_purchase_order,
    get_purchase_order,
    list_purchase_orders
)

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.post("/", response_model=PurchaseOrderOut)
async def create_po_endpoint(
    payload: PurchaseOrderCreate,
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    po = await create_purchase_order(
        session=session,
        organization_id=organization_id,
        vendor_id=payload.vendor_id,
        lines=payload.lines
    )
    return po


@router.get("/", response_model=list[PurchaseOrderOut])
async def list_pos_endpoint(
    organization_id: int = 1,
    session: AsyncSession = Depends(get_session),
):
    return await list_purchase_orders(session, organization_id)


@router.get("/{po_id}", response_model=PurchaseOrderOut)
async def get_po_endpoint(
    po_id: int,
    session: AsyncSession = Depends(get_session),
):
    po = await get_purchase_order(session, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    return po


@router.post("/{po_id}/receive")
async def receive_po_endpoint(
    po_id: int,
    location_id: int,  
    session: AsyncSession = Depends(get_session),
):
    await receive_purchase_order(session, po_id, location_id)
    return {"status": "received", "po_id": po_id}
