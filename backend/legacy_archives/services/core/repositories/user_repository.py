# backend/src/repositories/user_repository.py

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.org.app.user_models.models import User


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """
    Fetch a user by email (already normalized to lowercase by the caller).
    """
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Fetch a user by their UUID primary key.
    """
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
