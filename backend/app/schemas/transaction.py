from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    external_id: str | None = None
    provider: str = "manual"
    account_id: UUID | None = None
    credit_card_id: UUID | None = None
    bill_id: UUID | None = None
    date: datetime
    description: str
    amount: Decimal
    type: str | None = None
    payment_method: str | None = None
    category: str | None = None
    subcategory: str | None = None
    merchant: str | None = None
    is_recurring: bool = False
    raw_data: dict | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    external_id: str | None = None
    provider: str | None = None
    account_id: UUID | None = None
    credit_card_id: UUID | None = None
    bill_id: UUID | None = None
    date: datetime | None = None
    description: str | None = None
    amount: Decimal | None = None
    type: str | None = None
    payment_method: str | None = None
    category: str | None = None
    subcategory: str | None = None
    merchant: str | None = None
    is_recurring: bool | None = None
    raw_data: dict | None = None


class TransactionRead(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    created_at: datetime
    updated_at: datetime


class TransactionSearchRequest(BaseModel):
    query: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    category: str | None = None
    provider: str | None = None
    type: str | None = None
    limit: int = 50
