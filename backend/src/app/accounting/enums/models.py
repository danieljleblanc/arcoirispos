# backend/src/app/accounting/enums/models.py

from __future__ import annotations

from enum import Enum
from sqlalchemy import Enum as SAEnum


class AcctEntryTypeEnum(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


# --------------------------------------------------------------------
# SQLAlchemy-safe ENUM for mapped_column usage
# - Uses values_callable so DB stores pure strings
# - native_enum=False keeps migrations predictable
# - schema="acct" ensures the enum lives in correct schema
# --------------------------------------------------------------------
acct_entry_type_enum = SAEnum(
    AcctEntryTypeEnum,
    name="acct_entry_type_enum",
    values_callable=lambda x: [e.value for e in x],
    native_enum=False,
    schema="acct",
)


__all__ = [
    "AcctEntryTypeEnum",
    "acct_entry_type_enum",
]
