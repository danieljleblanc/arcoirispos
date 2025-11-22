# backend/src/api/locations_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.inv_schemas import (
    LocationCreate,
    LocationRead,
    LocationUpdate,
)
from src.services.inv.locations import location_service
from src.core.security.dependencies import require_any_staff, require_admin

router = APIRouter(prefix="/locations", tags=["locations"])


# ---------------------------------------------------------
# LIST LOCATIONS (any authenticated staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[LocationRead])
async def list_locations(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
    return await location_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE LOCATION (any authenticated staff)
# ---------------------------------------------------------
@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_any_staff),
):
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
    org_id: UUID,
    payload: LocationCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
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
    org_id: UUID,
    payload: LocationUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
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
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_admin),
):
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
