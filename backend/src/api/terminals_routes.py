from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.pos_schemas import (
    TerminalCreate,
    TerminalRead,
    TerminalUpdate,
)
from src.services.pos.terminals import terminal_service


router = APIRouter(prefix="/terminals", tags=["terminals"])


# ---- LIST BY ORG ----
@router.get("/", response_model=List[TerminalRead])
async def list_terminals(
    org_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await terminal_service.get_by_org(session, org_id, limit, offset)


# ---- GET SINGLE ----
@router.get("/{terminal_id}", response_model=TerminalRead)
async def get_terminal(
    terminal_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    terminal = await terminal_service.get_by_id(session, terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )
    return terminal


# ---- CREATE ----
@router.post("/", response_model=TerminalRead, status_code=status.HTTP_201_CREATED)
async def create_terminal(
    payload: TerminalCreate,
    session: AsyncSession = Depends(get_session),
):
    terminal = await terminal_service.create(session, payload.dict())
    await session.commit()
    await session.refresh(terminal)
    return terminal


# ---- UPDATE ----
@router.patch("/{terminal_id}", response_model=TerminalRead)
async def update_terminal(
    terminal_id: UUID,
    payload: TerminalUpdate,
    session: AsyncSession = Depends(get_session),
):
    terminal = await terminal_service.get_by_id(session, terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(terminal, field, value)

    await session.commit()
    await session.refresh(terminal)
    return terminal


# ---- DELETE ----
@router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terminal(
    terminal_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await terminal_service.delete(session, terminal_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found",
        )
    await session.commit()
