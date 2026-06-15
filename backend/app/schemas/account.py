from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    provider: str
    name: str
    type: str
    currency: str = "BRL"
    current_balance: Decimal = Decimal("0.00")
    institution_name: str | None = None
    branch: str | None = None
    account_number_masked: str | None = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    provider: str | None = None
    name: str | None = None
    type: str | None = None
    currency: str | None = None
    current_balance: Decimal | None = None
    institution_name: str | None = None
    branch: str | None = None
    account_number_masked: str | None = None


class AccountRead(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
