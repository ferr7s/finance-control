from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.credit_card import CreditCardCreate, CreditCardRead, CreditCardUpdate
from app.schemas.credit_card_bill import CreditCardBillCreate, CreditCardBillRead, CreditCardBillUpdate
from app.services import credit_cards_service

router = APIRouter(prefix="/api", tags=["credit cards"])


@router.get("/credit-cards", response_model=list[CreditCardRead])
def list_credit_cards(db: Session = Depends(get_db)):
    return credit_cards_service.list_credit_cards(db)


@router.post("/credit-cards", response_model=CreditCardRead, status_code=status.HTTP_201_CREATED)
def create_credit_card(payload: CreditCardCreate, db: Session = Depends(get_db)):
    return credit_cards_service.create_credit_card(db, payload)


@router.patch("/credit-cards/{card_id}", response_model=CreditCardRead)
def update_credit_card(card_id: UUID, payload: CreditCardUpdate, db: Session = Depends(get_db)):
    card = credit_cards_service.get_credit_card(db, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    return credit_cards_service.update_credit_card(db, card, payload)


@router.delete("/credit-cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credit_card(card_id: UUID, db: Session = Depends(get_db)):
    card = credit_cards_service.get_credit_card(db, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    credit_cards_service.delete_credit_card(db, card)


@router.get("/credit-cards/{card_id}/bills", response_model=list[CreditCardBillRead])
def list_bills(card_id: UUID, db: Session = Depends(get_db)):
    if not credit_cards_service.get_credit_card(db, card_id):
        raise HTTPException(status_code=404, detail="Credit card not found")
    return credit_cards_service.list_bills(db, card_id)


@router.post("/credit-cards/{card_id}/bills", response_model=CreditCardBillRead, status_code=status.HTTP_201_CREATED)
def create_bill(card_id: UUID, payload: CreditCardBillCreate, db: Session = Depends(get_db)):
    if not credit_cards_service.get_credit_card(db, card_id):
        raise HTTPException(status_code=404, detail="Credit card not found")
    return credit_cards_service.create_bill(db, card_id, payload)


@router.patch("/credit-card-bills/{bill_id}", response_model=CreditCardBillRead)
def update_bill(bill_id: UUID, payload: CreditCardBillUpdate, db: Session = Depends(get_db)):
    bill = credit_cards_service.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Credit card bill not found")
    return credit_cards_service.update_bill(db, bill, payload)


@router.delete("/credit-card-bills/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(bill_id: UUID, db: Session = Depends(get_db)):
    bill = credit_cards_service.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Credit card bill not found")
    credit_cards_service.delete_bill(db, bill)
