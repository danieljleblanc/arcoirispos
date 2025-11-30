from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.org.models.organization_settings_model import OrganizationSettings
from src.app.org.repositories.organization_settings_repository import (
    get_settings_by_org_id,
    update_settings,
    ensure_settings_exist,
)
from src.app.org.schemas.organization_settings_schema import (
    OrganizationSettingsUpdate,
)
from src.app.org.enums.models import (
    RoundingModeEnum,
    RoundingApplyToEnum,
    InventoryModeEnum,
)

# -------------------------------------------------------------------
# Allowed enum values (clean, Python-driven — never DB-driven)
# -------------------------------------------------------------------
ROUNDING_MODES = [e.value for e in RoundingModeEnum]
ROUNDING_TARGETS = [e.value for e in RoundingApplyToEnum]
INVENTORY_MODES = [e.value for e in InventoryModeEnum]


# ---------------------------------------------------------
# Get or create settings for an organization
# ---------------------------------------------------------
async def get_or_create_org_settings(
    session: AsyncSession,
    org_id: UUID,
) -> OrganizationSettings:
    return await ensure_settings_exist(session, org_id)


# ---------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------
def validate_rounding_mode(value: str | None):
    if value is not None and value not in ROUNDING_MODES:
        raise ValueError(f"Invalid rounding_mode: {value}")


def validate_rounding_apply_to(value: str | None):
    if value is not None and value not in ROUNDING_TARGETS:
        raise ValueError(f"Invalid rounding_apply_to: {value}")


def validate_inventory_mode(value: str | None):
    if value is not None and value not in INVENTORY_MODES:
        raise ValueError(f"Invalid inventory_mode: {value}")


# ---------------------------------------------------------
# Update organization settings — official service
# ---------------------------------------------------------
async def update_org_settings_service(
    session: AsyncSession,
    org_id: UUID,
    payload: OrganizationSettingsUpdate,
) -> OrganizationSettings:

    # Convert to dict and validate
    data = payload.dict(exclude_unset=True)

    validate_rounding_mode(data.get("rounding_mode"))
    validate_rounding_apply_to(data.get("rounding_apply_to"))
    validate_inventory_mode(data.get("inventory_mode"))

    # Auto-rules:
    if data.get("rounding_mode") == "none":
        data["rounding_apply_to"] = "none"

    if (
        data.get("rounding_mode")
        and data["rounding_mode"] != "none"
        and "rounding_apply_to" not in data
    ):
        data["rounding_apply_to"] = "cash_only"

    # Convert validated dict back into schema
    final_payload = OrganizationSettingsUpdate(**data)

    updated = await update_settings(session, org_id, final_payload)

    if not updated:
        raise RuntimeError("Failed to update organization settings")

    return updated
