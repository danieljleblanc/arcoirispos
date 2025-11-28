# backend/src/app/org/repositories/role_repository.py

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.org.models.role_models import UserOrgRole


async def get_roles_for_user_in_org(
    session: AsyncSession,
    user_id: UUID,
    org_id: UUID,
):
    """
    Return all UserOrgRole entries for a user in a specific organization.
    """
    stmt = select(UserOrgRole).where(
        UserOrgRole.user_id == user_id,
        UserOrgRole.org_id == org_id,
    )

    result = await session.execute(stmt)
    return result.scalars().all()
