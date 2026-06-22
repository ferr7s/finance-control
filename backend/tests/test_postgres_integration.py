import os
from collections.abc import Generator
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Account, CreditCard, CreditCardBill, Transaction  # noqa: F401


pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def postgres_engine() -> Generator[Engine, None, None]:
    admin_url_value = os.getenv("TEST_DATABASE_ADMIN_URL")
    if not admin_url_value:
        pytest.skip("TEST_DATABASE_ADMIN_URL is required for PostgreSQL integration tests")

    admin_url = make_url(admin_url_value)
    database_name = f"finance_control_test_{uuid4().hex}"
    test_url = admin_url.set(database=database_name)
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    engine = create_engine(test_url, pool_pre_ping=True)
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :database_name AND pid <> pg_backend_pid()"
                ),
                {"database_name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
        admin_engine.dispose()


@pytest.fixture()
def postgres_session(postgres_engine: Engine) -> Generator[Session, None, None]:
    connection = postgres_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


def test_postgres_preserves_transactions_when_financial_resources_are_deleted(postgres_session: Session):
    account = Account(provider="manual", name="Conta", type="checking", currency="BRL", current_balance=Decimal("100.00"))
    card = CreditCard(provider="manual", name="Cartao")
    postgres_session.add_all([account, card])
    postgres_session.commit()

    bill = CreditCardBill(
        credit_card_id=card.id,
        reference_month=date(2026, 6, 1),
        amount=Decimal("75.00"),
        status="open",
    )
    postgres_session.add(bill)
    postgres_session.commit()

    account_transaction = Transaction(
        provider="manual",
        account_id=account.id,
        date=datetime(2026, 6, 18, 12, 0),
        description="Compra na conta",
        amount=Decimal("-25.00"),
        type="expense",
    )
    card_transaction = Transaction(
        provider="manual",
        credit_card_id=card.id,
        bill_id=bill.id,
        date=datetime(2026, 6, 18, 13, 0),
        description="Compra no cartao",
        amount=Decimal("-75.00"),
        type="credit_card",
    )
    postgres_session.add_all([account_transaction, card_transaction])
    postgres_session.commit()

    postgres_session.delete(account)
    postgres_session.delete(bill)
    postgres_session.commit()
    postgres_session.expire_all()

    preserved_account_transaction = postgres_session.get(Transaction, account_transaction.id)
    preserved_card_transaction = postgres_session.get(Transaction, card_transaction.id)
    assert preserved_account_transaction is not None
    assert preserved_account_transaction.account_id is None
    assert preserved_card_transaction is not None
    assert preserved_card_transaction.credit_card_id == card.id
    assert preserved_card_transaction.bill_id is None

    replacement_bill = CreditCardBill(
        credit_card_id=card.id,
        reference_month=date(2026, 7, 1),
        amount=Decimal("50.00"),
        status="open",
    )
    card_transaction.bill = replacement_bill
    postgres_session.add(replacement_bill)
    postgres_session.commit()

    postgres_session.delete(card)
    postgres_session.commit()
    postgres_session.expire_all()

    preserved_card_transaction = postgres_session.get(Transaction, card_transaction.id)
    assert preserved_card_transaction is not None
    assert preserved_card_transaction.credit_card_id is None
    assert preserved_card_transaction.bill_id is None
    assert postgres_session.get(CreditCardBill, replacement_bill.id) is None


def test_postgres_enforces_provider_external_id_uniqueness(postgres_session: Session):
    first = Transaction(
        external_id="duplicate-1",
        provider="manual",
        date=datetime(2026, 6, 18, 12, 0),
        description="Primeira importacao",
        amount=Decimal("-10.00"),
        type="expense",
    )
    postgres_session.add(first)
    postgres_session.commit()

    duplicate = Transaction(
        external_id="duplicate-1",
        provider="manual",
        date=datetime(2026, 6, 18, 13, 0),
        description="Importacao duplicada",
        amount=Decimal("-10.00"),
        type="expense",
    )
    postgres_session.add(duplicate)

    with pytest.raises(IntegrityError):
        postgres_session.commit()
    postgres_session.rollback()

    transactions = postgres_session.scalars(
        select(Transaction).where(Transaction.provider == "manual", Transaction.external_id == "duplicate-1")
    ).all()
    assert [transaction.id for transaction in transactions] == [first.id]
