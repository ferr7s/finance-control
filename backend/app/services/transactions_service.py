from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionSearchRequest, TransactionUpdate
from app.utils.categorizer import categorize_transaction, infer_transaction_type


def _apply_filters(
    stmt: Select[tuple[Transaction]],
    query: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
    provider: str | None = None,
    type: str | None = None,
) -> Select[tuple[Transaction]]:
    filters = []
    if query:
        pattern = f"%{query}%"
        filters.append(or_(Transaction.description.ilike(pattern), Transaction.merchant.ilike(pattern)))
    if start_date:
        filters.append(Transaction.date >= start_date)
    if end_date:
        filters.append(Transaction.date <= end_date)
    if category:
        filters.append(Transaction.category == category)
    if provider:
        filters.append(Transaction.provider == provider)
    if type:
        filters.append(Transaction.type == type)
    if filters:
        stmt = stmt.where(and_(*filters))
    return stmt


def list_transactions(
    db: Session,
    query: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
    provider: str | None = None,
    type: str | None = None,
    limit: int = 200,
) -> list[Transaction]:
    stmt = select(Transaction).order_by(Transaction.date.desc()).limit(min(limit, 500))
    stmt = _apply_filters(stmt, query, start_date, end_date, category, provider, type)
    return list(db.scalars(stmt).all())


def search_transactions(db: Session, payload: TransactionSearchRequest) -> list[Transaction]:
    return list_transactions(db, **payload.model_dump())


def get_transaction(db: Session, transaction_id: UUID) -> Transaction | None:
    return db.get(Transaction, transaction_id)


def find_duplicate(db: Session, provider: str, external_id: str | None) -> Transaction | None:
    if not external_id:
        return None
    stmt = select(Transaction).where(Transaction.provider == provider, Transaction.external_id == external_id)
    return db.scalar(stmt)


def create_transaction(db: Session, payload: TransactionCreate) -> Transaction:
    data = payload.model_dump()
    if find_duplicate(db, data["provider"], data.get("external_id")):
        raise ValueError("Duplicate transaction")
    amount = Decimal(data["amount"])
    data["category"] = data.get("category") or categorize_transaction(data["description"])
    data["type"] = infer_transaction_type(amount, data["description"], data.get("type"))
    transaction = Transaction(**data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(db: Session, transaction: Transaction, payload: TransactionUpdate) -> Transaction:
    data = payload.model_dump(exclude_unset=True)
    if "description" in data and not data.get("category") and transaction.category in {None, "outros"}:
        data["category"] = categorize_transaction(data["description"])
    if "amount" in data or "description" in data or "type" in data:
        amount = Decimal(data.get("amount", transaction.amount))
        description = data.get("description", transaction.description)
        data["type"] = infer_transaction_type(amount, description, data.get("type", transaction.type))
    for key, value in data.items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()


def category_totals(db: Session, start_date: datetime | None = None, end_date: datetime | None = None) -> list[tuple[str, Decimal]]:
    stmt = select(Transaction.category, func.sum(func.abs(Transaction.amount))).where(Transaction.type == "expense")
    if start_date:
        stmt = stmt.where(Transaction.date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.date < end_date)
    stmt = stmt.group_by(Transaction.category).order_by(func.sum(func.abs(Transaction.amount)).desc())
    return [(category or "outros", amount or Decimal("0.00")) for category, amount in db.execute(stmt).all()]
