# backend/src/app/org/repositories/user_repository.py

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.org.models.user_models import User


async def get_user_by_id(
    session: AsyncSession,
    user_id: UUID,
) -> Optional[User]:
    """
    Return a user by primary key (user_id).
    """
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> Optional[User]:
    """
    Return a user by email (case-insensitive because CITEXT).
    """
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
