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

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=List[LocationRead])
async def list_locations(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await location_service.get_by_org(session, org_id, limit, offset)


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    location = await location_service.get_by_id(session, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )
    return location


@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    session: AsyncSession = Depends(get_session),
):
    location = await location_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(location)
    return location


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: UUID,
    payload: LocationUpdate,
    session: AsyncSession = Depends(get_session),
):
    location = await location_service.get_by_id(session, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(location, field, value)

    await session.commit()
    await session.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await location_service.delete_location(session, location_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    await session.commit()
    return None
