# backend/src/schemas/inv_schemas.py

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ====================================================
# ITEMS
# ====================================================

class ItemBase(BaseModel):
    name: str
    item_type: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    default_price: Decimal = Decimal("0")
    cost_basis: Optional[Decimal] = None
    tax_id: Optional[UUID] = None
    is_active: bool = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    item_type: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    default_price: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    tax_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ItemRead(ItemBase):
    item_id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ====================================================
# LOCATIONS
# ====================================================

class LocationBase(BaseModel):
    name: str
    code: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class LocationRead(LocationBase):
    location_id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ====================================================
# STOCK LEVELS
# ====================================================

class StockLevelBase(BaseModel):
    item_id: UUID
    location_id: UUID
    quantity_on_hand: Decimal


class StockLevelCreate(StockLevelBase):
    pass


class StockLevelUpdate(BaseModel):
    quantity_on_hand: Optional[Decimal] = None


class StockLevelRead(BaseModel):
    stock_level_id: UUID
    org_id: UUID
    item_id: UUID
    location_id: UUID
    quantity_on_hand: Decimal
    updated_at: datetime

    model_config = {"from_attributes": True}


# ====================================================
# STOCK MOVEMENTS
# ====================================================

class StockMovementBase(BaseModel):
    item_id: UUID
    location_id: UUID
    source_type: str
    source_id: Optional[UUID] = None
    quantity_delta: Decimal
    unit_cost: Optional[Decimal] = None
    occurred_at: datetime


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementRead(StockMovementBase):
    movement_id: UUID
    org_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ====================================================
# STOCK ADJUSTMENTS
# ====================================================

class StockAdjustmentBase(BaseModel):
    item_id: UUID
    location_id: UUID
    quantity_delta: Decimal
    reason: str = Field(..., description="Required reason for admin adjustment")


class StockAdjustmentCreate(StockAdjustmentBase):
    pass


class StockAdjustmentRead(StockAdjustmentBase):
    org_id: UUID
    movement_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
