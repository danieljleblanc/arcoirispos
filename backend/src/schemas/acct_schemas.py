# backend/src/schemas/acct_schemas.py

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# -------- Chart of Accounts --------

class AccountBase(BaseModel):
    org_id: UUID
    code: str
    name: str
    type: str   # 'asset','liability','equity','revenue','expense'
    subtype: Optional[str] = None
    is_active: bool = True
    parent_id: Optional[UUID] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[UUID] = None


class AccountRead(AccountBase):
    account_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------- Journal Lines --------

class JournalLineBase(BaseModel):
    org_id: UUID
    line_number: int
    account_id: UUID
    entry_type: str  # 'debit' or 'credit'
    amount: Decimal
    memo: Optional[str] = None


class JournalLineCreate(JournalLineBase):
    pass


class JournalLineRead(JournalLineBase):
    journal_line_id: UUID
    journal_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# -------- Journal Entries --------

class JournalEntryBase(BaseModel):
    org_id: UUID
    journal_number: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None
    description: Optional[str] = None
    journal_date: date
    posted: bool = False
    created_by: Optional[UUID] = None


class JournalEntryCreate(JournalEntryBase):
    lines: list[JournalLineCreate]


class JournalEntryRead(JournalEntryBase):
    journal_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class JournalEntryReadWithLines(JournalEntryRead):
    lines: list[JournalLineRead]
