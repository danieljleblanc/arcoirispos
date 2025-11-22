from fastapi import APIRouter, Depends, status, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime, timezone

from src.core.database import get_session
from src.models.core.user_models import User
from src.models.core.organization_models import Organization
from src.models.core.role_models import UserOrgRole
from src.core.security.hashing import hash_password
from src.core.config import settings


router = APIRouter(prefix="/dev", tags=["dev-tools"])


# ---------------------------------------------------------
# SECURITY: lock dev-only routes behind a secret header
# ---------------------------------------------------------
async def verify_dev_secret(x_dev_secret: str = Header(None)):
    """
    Protects dev-only routes using a secret from .env.
    Requires header:  X-DEV-SECRET: <value>
    """

    expected = settings.dev_admin_secret

    if expected is None or expected.strip() == "":
        raise HTTPException(
            status_code=500,
            detail="DEV_ADMIN_SECRET not configured",
        )

    if x_dev_secret != expected:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: invalid dev secret",
        )


# ---------------------------------------------------------
# DEV BOOTSTRAP: Create Admin
# ---------------------------------------------------------
@router.post(
    "/create-admin",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_dev_secret)],
)
async def create_admin_user(
    session: AsyncSession = Depends(get_session),
):
    """
    Creates a development admin user.
    Safe to run multiple times — if the user exists, returns it.
    """

    admin_email = "admin@example.com"
    now = datetime.now(timezone.utc)

    # -----------------------------
    # 1. Ensure at least one org exists
    # -----------------------------
    org_result = await session.execute(select(Organization))
    org = org_result.scalar_one_or_none()

    if not org:
        org = Organization(
            org_id=uuid4(),
            name="Dev Organization",
            legal_name="Dev Organization",
            timezone="UTC",
            base_currency="USD",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        session.add(org)
        await session.flush()

    # -----------------------------
    # 2. Check if admin user already exists
    # -----------------------------
    stmt = select(User).where(User.email == admin_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return {
            "message": "Admin already exists",
            "user_id": str(user.user_id),
            "email": user.email,
            "org_id": str(org.org_id),
        }

    # -----------------------------
    # 3. Create new admin user
    # -----------------------------
    admin = User(
        email=admin_email,
        display_name="Dev Admin",
        password_hash=hash_password("password123"),
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    session.add(admin)
    await session.flush()

    # -----------------------------
    # 4. Assign RBAC role: OWNER
    # -----------------------------
    owner_role = UserOrgRole(
        user_org_role_id=uuid4(),
        user_id=admin.user_id,
        org_id=org.org_id,
        role="owner",
        is_primary=True,
        created_at=now,
    )

    session.add(owner_role)
    await session.commit()
    await session.refresh(admin)

    return {
        "message": "Admin created",
        "user_id": str(admin.user_id),
        "email": admin.email,
        "org_id": str(org.org_id),
    }
