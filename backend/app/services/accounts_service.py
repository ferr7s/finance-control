from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


def list_accounts(db: Session) -> list[Account]:
    return list(db.scalars(select(Account).order_by(Account.name)).all())


def get_account(db: Session, account_id: UUID) -> Account | None:
    return db.get(Account, account_id)


def create_account(db: Session, payload: AccountCreate) -> Account:
    account = Account(**payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(db: Session, account: Account, payload: AccountUpdate) -> Account:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account: Account) -> None:
    db.delete(account)
    db.commit()
