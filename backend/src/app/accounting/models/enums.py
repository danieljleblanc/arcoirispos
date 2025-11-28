# backend/src/app/accounting/models/enum.py

from sqlalchemy.dialects import postgresql

# -----------------------------------------------------------
# Accounting entry type ENUM
# -----------------------------------------------------------
# Must match DB type name created by your initial migration.
# Used by JournalEntry and JournalLine models.
# -----------------------------------------------------------

acct_entry_type_enum = postgresql.ENUM(
    "debit",
    "credit",
    name="acct_entry_type_enum",   # ✅ corrected type name
    schema="acct",
    create_type=False,             # DB type already created in migrations
)
