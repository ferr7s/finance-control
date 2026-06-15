from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services import transactions_service

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    query: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
    provider: str | None = None,
    type: str | None = Query(default=None),
    limit: int = 200,
    db: Session = Depends(get_db),
):
    return transactions_service.list_transactions(db, query, start_date, end_date, category, provider, type, limit)


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    try:
        return transactions_service.create_transaction(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: UUID, payload: TransactionUpdate, db: Session = Depends(get_db)):
    transaction = transactions_service.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transactions_service.update_transaction(db, transaction, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: UUID, db: Session = Depends(get_db)):
    transaction = transactions_service.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transactions_service.delete_transaction(db, transaction)
