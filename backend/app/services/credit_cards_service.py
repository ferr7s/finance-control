from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.credit_card import CreditCard
from app.models.credit_card_bill import CreditCardBill
from app.schemas.credit_card import CreditCardCreate, CreditCardUpdate
from app.schemas.credit_card_bill import CreditCardBillCreate, CreditCardBillUpdate


def list_credit_cards(db: Session) -> list[CreditCard]:
    return list(db.scalars(select(CreditCard).order_by(CreditCard.name)).all())


def get_credit_card(db: Session, card_id: UUID) -> CreditCard | None:
    return db.get(CreditCard, card_id)


def create_credit_card(db: Session, payload: CreditCardCreate) -> CreditCard:
    card = CreditCard(**payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def update_credit_card(db: Session, card: CreditCard, payload: CreditCardUpdate) -> CreditCard:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(card, key, value)
    db.commit()
    db.refresh(card)
    return card


def delete_credit_card(db: Session, card: CreditCard) -> None:
    db.delete(card)
    db.commit()


def list_bills(db: Session, card_id: UUID) -> list[CreditCardBill]:
    stmt = select(CreditCardBill).where(CreditCardBill.credit_card_id == card_id).order_by(CreditCardBill.reference_month.desc())
    return list(db.scalars(stmt).all())


def get_bill(db: Session, bill_id: UUID) -> CreditCardBill | None:
    return db.get(CreditCardBill, bill_id)


def create_bill(db: Session, card_id: UUID, payload: CreditCardBillCreate) -> CreditCardBill:
    bill = CreditCardBill(credit_card_id=card_id, **payload.model_dump())
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def update_bill(db: Session, bill: CreditCardBill, payload: CreditCardBillUpdate) -> CreditCardBill:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(bill, key, value)
    db.commit()
    db.refresh(bill)
    return bill


def delete_bill(db: Session, bill: CreditCardBill) -> None:
    db.delete(bill)
    db.commit()
