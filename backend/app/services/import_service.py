from io import StringIO

from sqlalchemy.orm import Session

from app.schemas.transaction import TransactionCreate
from app.services.transactions_service import create_transaction
from app.utils.csv_parser import parse_bank_csv


def import_bank_csv(db: Session, content: bytes) -> dict[str, int | list[str]]:
    text = content.decode("utf-8-sig")
    rows = parse_bank_csv(StringIO(text))
    imported = 0
    ignored = 0
    errors: list[str] = []

    for index, row in enumerate(rows, start=1):
        try:
            payload = TransactionCreate(
                external_id=str(row["external_id"]),
                provider=str(row["provider"]),
                date=row["date"],
                description=str(row["description"]),
                amount=row["amount"],
                type=str(row["type"]),
                payment_method=str(row["payment_method"]),
                category=str(row["category"]),
                raw_data={key: str(value) for key, value in row.items()},
            )
            create_transaction(db, payload)
            imported += 1
        except ValueError:
            ignored += 1
        except Exception as exc:  # noqa: BLE001 - import must return row-level errors
            ignored += 1
            errors.append(f"Linha {index}: {exc}")

    return {
        "total_rows": len(rows),
        "imported": imported,
        "ignored": ignored,
        "errors": errors,
    }
