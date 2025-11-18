from sqlalchemy.dialects import postgresql

acct_entry_type_enum = postgresql.ENUM(
    "debit",
    "credit",
    name="acct_entry_type",
    create_type=False,  # DB type is created via migrations
)
