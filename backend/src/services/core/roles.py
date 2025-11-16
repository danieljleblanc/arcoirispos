from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import UserOrgRole


class RoleService:
    async def get_roles_for_user(self, session: AsyncSession, user_id):
        stmt = select(UserOrgRole.role).where(UserOrgRole.user_id == user_id)
        rows = (await session.execute(stmt)).scalars().all()
        return rows


role_service = RoleService()
