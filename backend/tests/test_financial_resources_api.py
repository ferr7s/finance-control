from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models import Account, CreditCard, CreditCardBill, Transaction  # noqa: F401


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def test_accounts_crud(client: TestClient):
    create_response = client.post(
        "/api/accounts",
        json={
            "provider": "manual",
            "name": "Conta Corrente",
            "type": "checking",
            "currency": "BRL",
            "current_balance": "1234.56",
            "institution_name": "Banco Teste",
            "branch": "0001",
            "account_number_masked": "****1234",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Conta Corrente"
    assert Decimal(created["current_balance"]) == Decimal("1234.56")

    list_response = client.get("/api/accounts")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [created["id"]]

    update_response = client.patch(
        f"/api/accounts/{created['id']}",
        json={"name": "Reserva", "current_balance": "2000.00"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Reserva"
    assert Decimal(update_response.json()["current_balance"]) == Decimal("2000.00")

    assert client.patch("/api/accounts/00000000-0000-0000-0000-000000000000", json={"name": "Missing"}).status_code == 404
    assert client.delete(f"/api/accounts/{created['id']}").status_code == 204
    assert client.get("/api/accounts").json() == []


def test_deleting_account_preserves_associated_transactions(client: TestClient):
    account = client.post(
        "/api/accounts",
        json={
            "provider": "manual",
            "name": "Conta Corrente",
            "type": "checking",
            "currency": "BRL",
            "current_balance": "100.00",
        },
    ).json()
    transaction = client.post(
        "/api/transactions",
        json={
            "provider": "manual",
            "account_id": account["id"],
            "date": "2026-06-18T12:00:00",
            "description": "Compra preservada",
            "amount": "-25.00",
        },
    ).json()

    assert client.delete(f"/api/accounts/{account['id']}").status_code == 204

    transactions = client.get("/api/transactions").json()
    assert [item["id"] for item in transactions] == [transaction["id"]]
    assert transactions[0]["account_id"] is None


def test_credit_cards_and_bills_crud(client: TestClient):
    card_response = client.post(
        "/api/credit-cards",
        json={
            "provider": "manual",
            "name": "Cartao Principal",
            "brand": "Visa",
            "limit_total": "5000.00",
            "limit_available": "3500.00",
            "closing_day": 20,
            "due_day": 27,
        },
    )

    assert card_response.status_code == 201
    card = card_response.json()
    assert card["name"] == "Cartao Principal"

    updated_card = client.patch(
        f"/api/credit-cards/{card['id']}",
        json={"limit_available": "3200.00", "due_day": 28},
    )
    assert updated_card.status_code == 200
    assert Decimal(updated_card.json()["limit_available"]) == Decimal("3200.00")
    assert updated_card.json()["due_day"] == 28

    bill_response = client.post(
        f"/api/credit-cards/{card['id']}/bills",
        json={
            "reference_month": "2026-06-01",
            "due_date": "2026-06-27",
            "closing_date": "2026-06-20",
            "amount": "845.90",
            "status": "open",
        },
    )
    assert bill_response.status_code == 201
    bill = bill_response.json()
    assert bill["credit_card_id"] == card["id"]
    assert Decimal(bill["amount"]) == Decimal("845.90")

    bills_response = client.get(f"/api/credit-cards/{card['id']}/bills")
    assert bills_response.status_code == 200
    assert [item["id"] for item in bills_response.json()] == [bill["id"]]

    updated_bill = client.patch(f"/api/credit-card-bills/{bill['id']}", json={"status": "paid", "amount": "800.00"})
    assert updated_bill.status_code == 200
    assert updated_bill.json()["status"] == "paid"
    assert Decimal(updated_bill.json()["amount"]) == Decimal("800.00")

    assert client.get("/api/credit-cards/00000000-0000-0000-0000-000000000000/bills").status_code == 404
    assert client.delete(f"/api/credit-card-bills/{bill['id']}").status_code == 204
    assert client.delete(f"/api/credit-cards/{card['id']}").status_code == 204
    assert client.get("/api/credit-cards").json() == []


def test_deleting_credit_card_preserves_transactions_and_removes_bills(client: TestClient):
    card = client.post(
        "/api/credit-cards",
        json={
            "provider": "manual",
            "name": "Cartao Principal",
            "brand": "Visa",
        },
    ).json()
    bill = client.post(
        f"/api/credit-cards/{card['id']}/bills",
        json={
            "reference_month": "2026-06-01",
            "amount": "125.00",
            "status": "open",
        },
    ).json()
    transaction = client.post(
        "/api/transactions",
        json={
            "provider": "manual",
            "credit_card_id": card["id"],
            "bill_id": bill["id"],
            "date": "2026-06-18T12:00:00",
            "description": "Compra no cartao",
            "amount": "-125.00",
        },
    ).json()

    assert client.delete(f"/api/credit-cards/{card['id']}").status_code == 204

    transactions = client.get("/api/transactions").json()
    assert [item["id"] for item in transactions] == [transaction["id"]]
    assert transactions[0]["credit_card_id"] is None
    assert transactions[0]["bill_id"] is None
    assert client.patch(f"/api/credit-card-bills/{bill['id']}", json={"status": "paid"}).status_code == 404


def test_deleting_bill_preserves_associated_transactions(client: TestClient):
    card = client.post(
        "/api/credit-cards",
        json={
            "provider": "manual",
            "name": "Cartao Principal",
            "brand": "Visa",
        },
    ).json()
    bill = client.post(
        f"/api/credit-cards/{card['id']}/bills",
        json={
            "reference_month": "2026-06-01",
            "amount": "75.00",
            "status": "open",
        },
    ).json()
    transaction = client.post(
        "/api/transactions",
        json={
            "provider": "manual",
            "credit_card_id": card["id"],
            "bill_id": bill["id"],
            "date": "2026-06-18T12:00:00",
            "description": "Compra da fatura",
            "amount": "-75.00",
        },
    ).json()

    assert client.delete(f"/api/credit-card-bills/{bill['id']}").status_code == 204

    transactions = client.get("/api/transactions").json()
    assert [item["id"] for item in transactions] == [transaction["id"]]
    assert transactions[0]["credit_card_id"] == card["id"]
    assert transactions[0]["bill_id"] is None
