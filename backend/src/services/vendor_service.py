from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.models.vendor import Vendor


# ─────────────────────────────────────────────
# CREATE VENDOR
# ─────────────────────────────────────────────
async def create_vendor(session: AsyncSession, organization_id: int, name: str,
                        contact_name: str | None, email: str | None, phone: str | None):

    vendor = Vendor(
        name=name,
        contact_name=contact_name,
        email=email,
        phone=phone,
        organization_id=organization_id
    )
    session.add(vendor)
    await session.commit()
    await session.refresh(vendor)
    return vendor


# ─────────────────────────────────────────────
# GET VENDOR
# ─────────────────────────────────────────────
async def get_vendor(session: AsyncSession, vendor_id: int):
    return await session.get(Vendor, vendor_id)


# ─────────────────────────────────────────────
# LIST VENDORS
# ─────────────────────────────────────────────
async def list_vendors(session: AsyncSession, organization_id: int):
    result = await session.execute(
        select(Vendor).where(Vendor.organization_id == organization_id)
    )
    return result.scalars().all()


# ─────────────────────────────────────────────
# UPDATE VENDOR
# ─────────────────────────────────────────────
async def update_vendor(session: AsyncSession, vendor_id: int, **fields):
    result = await session.execute(
        update(Vendor)
        .where(Vendor.id == vendor_id)
        .values(**fields)
        .returning(Vendor)
    )

    vendor = result.fetchone()
    if not vendor:
        return None

    await session.commit()
    return vendor[0]


# ─────────────────────────────────────────────
# DELETE VENDOR
# ─────────────────────────────────────────────
async def delete_vendor(session: AsyncSession, vendor_id: int):
    await session.execute(
        delete(Vendor).where(Vendor.id == vendor_id)
    )
    await session.commit()
    return True
