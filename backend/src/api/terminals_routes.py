# backend/src/api/terminals_routes.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security.dependencies import require_any_staff, require_admin
from src.schemas.pos_schemas import (
    TerminalCreate,
    TerminalRead,
    TerminalUpdate,
)
from src.services.pos.terminals import terminal_service


router = APIRouter(prefix="/terminals", tags=["terminals"])


# ---------------------------------------------------------
# LIST TERMINALS (any staff)
# ---------------------------------------------------------
@router.get("/", response_model=List[TerminalRead])
async def list_terminals(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_any_staff),
):
    return await terminal_service.get_by_org(session, org_id, limit, offset)


# ---------------------------------------------------------
# GET SINGLE TERMINAL (any staff)
# ---------------------------------------------------------
@router.get("/{terminal_id}", response_model=TerminalRead)
async def get_terminal(
    terminal_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_any_staff),
):
    terminal = await terminal_service.get_by_id(session, terminal_id)

    if not terminal or terminal.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )

    return terminal


# ---------------------------------------------------------
# CREATE TERMINAL (admin / manager / owner)
# ---------------------------------------------------------
@router.post("/", response_model=TerminalRead, status_code=status.HTTP_201_CREATED)
async def create_terminal(
    payload: TerminalCreate,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_admin),
):
    terminal = await terminal_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(terminal)
    return terminal


# ---------------------------------------------------------
# UPDATE TERMINAL (admin / manager / owner)
# ---------------------------------------------------------
@router.patch("/{terminal_id}", response_model=TerminalRead)
async def update_terminal(
    terminal_id: UUID,
    payload: TerminalUpdate,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_admin),
):
    terminal = await terminal_service.get_by_id(session, terminal_id)

    if not terminal or terminal.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(terminal, field, value)

    await session.commit()
    await session.refresh(terminal)
    return terminal


# ---------------------------------------------------------
# DELETE TERMINAL (admin / manager / owner)
# ---------------------------------------------------------
@router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terminal(
    terminal_id: UUID,
    org_id: UUID,
    session: AsyncSession = Depends(get_session),
    user = Depends(require_admin),
):
    terminal = await terminal_service.get_by_id(session, terminal_id)

    if not terminal or terminal.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )

    deleted = await terminal_service.delete(session, terminal_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )

    await session.commit()
    return None
