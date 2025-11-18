# backend/src/api/dev_bootstrap_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_session
from src.models.models import User
from src.core.security.hashing import hash_password

router = APIRouter(prefix="/dev", tags=["dev-tools"])


@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    session: AsyncSession = Depends(get_session),
):
    """
    Creates a development admin user.
    Safe to run multiple times — if the user exists, returns it.
    """

    admin_email = "admin@example.com"

    # Check if exists
    stmt = select(User).where(User.email == admin_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return {
            "message": "Admin already exists",
            "user_id": str(user.user_id),
            "email": user.email,
        }

    # Create new admin
    admin = User(
        email=admin_email,
        display_name="Dev Admin",
        password_hash=hash_password("password123"),
        role="owner",
    )

    session.add(admin)
    await session.commit()
    await session.refresh(admin)

    return {
        "message": "Admin created",
        "user_id": str(admin.user_id),
        "email": admin.email,
    }
