# backend/src/services/acct/accounts.py

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ChartOfAccount
from src.services.base_repository import BaseRepository


class AccountService(BaseRepository[ChartOfAccount]):
    def __init__(self) -> None:
        super().__init__(ChartOfAccount)

    async def get_by_org(
        self,
        session: AsyncSession,
        org_id: UUID,
    ) -> List[ChartOfAccount]:
        stmt = (
            select(ChartOfAccount)
            .where(ChartOfAccount.org_id == org_id)
            .order_by(ChartOfAccount.code.asc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()


account_service = AccountService()
