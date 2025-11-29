# backend/src/app/org/schemas/organization_settings_schema.py

from typing import Literal, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


# ---------------------------------------------
# Allowed enum values
# ---------------------------------------------

RoundingMode = Literal["none", "nickel", "dime", "quarter", "dollar"]
RoundingApplyTo = Literal["none", "cash_only", "all_payments"]
InventoryMode = Literal["deduct_on_cart", "deduct_on_sale"]


# ---------------------------------------------
# READ SCHEMA (what API returns)
# ---------------------------------------------
class OrganizationSettingsRead(BaseModel):
    settings_id: UUID
    org_id: UUID

    rounding_mode: RoundingMode
    rounding_apply_to: RoundingApplyTo

    inventory_mode: InventoryMode

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # allows SQLAlchemy → Pydantic conversion


# ---------------------------------------------
# UPDATE SCHEMA (partial update)
# ---------------------------------------------
class OrganizationSettingsUpdate(BaseModel):
    rounding_mode: Optional[RoundingMode] = None
    rounding_apply_to: Optional[RoundingApplyTo] = None
    inventory_mode: Optional[InventoryMode] = None


# ---------------------------------------------
# CREATE SCHEMA (used internally during org creation)
# ---------------------------------------------
class OrganizationSettingsCreate(BaseModel):
    rounding_mode: Optional[RoundingMode] = "none"
    rounding_apply_to: Optional[RoundingApplyTo] = "cash_only"
    inventory_mode: Optional[InventoryMode] = "deduct_on_cart"
