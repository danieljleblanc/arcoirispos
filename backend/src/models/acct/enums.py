from sqlalchemy.dialects import postgresql

acct_entry_type_enum = postgresql.ENUM(
    "debit",
    "credit",
    name="acct_entry_type",
    schema="acct",
    create_type=False,  # keep this because the init migration creates it
)
