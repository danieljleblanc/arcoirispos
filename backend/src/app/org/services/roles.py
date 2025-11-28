# backend/src/app/org/services/roles.py

from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.org.models.role_models import UserOrgRole


class RoleService:
    async def get_roles_for_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        org_id: Optional[UUID] = None,
    ) -> List[str]:
        """
        Return a list of role strings for a user.
        If org_id is provided, return roles ONLY for that organization.
        """

        stmt = select(UserOrgRole.role).where(UserOrgRole.user_id == user_id)

        if org_id:
            stmt = stmt.where(UserOrgRole.org_id == org_id)

        result = await session.execute(stmt)
        return result.scalars().all()


role_service = RoleService()
