# backend/src/app/accounting/enums/enum.py

from __future__ import annotations

from enum import Enum
from sqlalchemy import Enum as SAEnum


class AcctEntryTypeEnum(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


# --------------------------------------------------------------
# SQLAlchemy-safe ENUM factory (NOT executed at import time)
# --------------------------------------------------------------
def get_acct_entry_type_enum():
    return SAEnum(
        AcctEntryTypeEnum,
        name="acct_entry_type_enum",
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        schema="acct",
    )


__all__ = [
    "AcctEntryTypeEnum",
    "get_acct_entry_type_enum",
]
