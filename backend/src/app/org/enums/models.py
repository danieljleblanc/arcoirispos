# backend/src/app/org/enums/models.py

from __future__ import annotations

from enum import Enum
from sqlalchemy import Enum as SAEnum


# -----------------------------
# Python Enum definitions
# -----------------------------

class RoundingModeEnum(str, Enum):
    NONE = "none"
    NICKEL = "nickel"
    DIME = "dime"
    QUARTER = "quarter"
    DOLLAR = "dollar"


class InventoryModeEnum(str, Enum):
    DEDUCT_ON_CART = "deduct_on_cart"
    DEDUCT_ON_SALE = "deduct_on_sale"


class RoundingApplyToEnum(str, Enum):
    NONE = "none"
    CASH_ONLY = "cash_only"
    ALL_PAYMENTS = "all_payments"


# -----------------------------
# SQLAlchemy-safe Enum factories
# -----------------------------

def get_rounding_mode_enum():
    return SAEnum(
        RoundingModeEnum,
        name="rounding_mode",
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        schema="core",
    )


def get_rounding_apply_to_enum():
    return SAEnum(
        RoundingApplyToEnum,
        name="rounding_apply_to",
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        schema="core",
    )


def get_inventory_mode_enum():
    return SAEnum(
        InventoryModeEnum,
        name="inventory_mode",
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        schema="core",
    )


__all__ = [
    "RoundingModeEnum",
    "RoundingApplyToEnum",
    "InventoryModeEnum",
    "get_rounding_mode_enum",
    "get_rounding_apply_to_enum",
    "get_inventory_mode_enum",
]
