# backend/src/app/inventory/routes/locations_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_session

# ---------------------------------------------------------
# ✔️ Corrected security import paths (must be under src.app)
# ---------------------------------------------------------
from src.app.auth.services.org_context import get_current_org
from src.app.auth.services.dependencies import (
    require_any_staff_org,
    require_admin_org,
)

from src.app.inventory.schemas.inv_schemas import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
)

from src.app.inventory.services.location_service import location_service

router = APIRouter(prefix="/locations", tags=["locations"])


# ---------------------------------------------------------
# LIST LOCATIONS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[LocationRead])
async def list_locations(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    return await location_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE LOCATION (any staff)
# ---------------------------------------------------------
@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_any_staff_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    location = await location_service.get_by_id(session, location_id)

    if not location or location.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    return location


# ---------------------------------------------------------
# CREATE LOCATION (admin/manager/owner)
# ---------------------------------------------------------
@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)

    data = payload.dict()
    data["org_id"] = org_id

    location = await location_service.create(session, data)
    await session.commit()
    await session.refresh(location)
    return location


# ---------------------------------------------------------
# UPDATE LOCATION (admin/manager/owner)
# ---------------------------------------------------------
@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: UUID,
    payload: LocationUpdate,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    location = await location_service.get_by_id(session, location_id)

    if not location or location.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    update_fields = payload.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(location, field, value)

    await session.commit()
    await session.refresh(location)
    return location


# ---------------------------------------------------------
# DELETE LOCATION (admin/manager/owner)
# ---------------------------------------------------------
@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: UUID,
    session: AsyncSession = Depends(get_session),
    org_ctx = Depends(get_current_org),
    user    = Depends(require_admin_org),
):
    org_id = getattr(org_ctx, "org_id", None)
    location = await location_service.get_by_id(session, location_id)

    if not location or location.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    deleted = await location_service.delete_location(session, location_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete location",
        )

    await session.commit()
    return None
