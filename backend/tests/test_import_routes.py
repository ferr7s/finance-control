from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Account, CreditCard, CreditCardBill, Transaction  # noqa: F401


def test_preview_bank_csv_endpoint():
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
        client = TestClient(app)
        content = "data;descricao;valor;banco\n01/06/2026;Padaria;-18,90;Nubank\n"

        response = client.post(
            "/api/import/bank-csv/preview",
            files={"file": ("transactions.csv", content, "text/csv")},
        )

        assert response.status_code == 200
        preview = response.json()
        assert preview["total_rows"] == 1
        assert preview["importable"] == 1
        assert preview["duplicates"] == 0
        assert preview["errors"] == []
        assert preview["sample_rows"][0]["status"] == "ready"
        assert preview["sample_rows"][0]["description"] == "Padaria"
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
