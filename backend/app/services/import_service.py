from io import StringIO

from sqlalchemy.orm import Session

from app.schemas.transaction import TransactionCreate
from app.services.transactions_service import create_transaction, find_duplicate
from app.utils.csv_parser import parse_bank_csv
from app.utils.ofx_parser import parse_ofx


def _parse_csv_content(content: bytes) -> list[dict[str, object]]:
    text = content.decode("utf-8-sig")
    return parse_bank_csv(StringIO(text))


def _preview_row(row: dict[str, object], status: str) -> dict[str, str]:
    return {
        "status": status,
        "external_id": str(row["external_id"]),
        "date": row["date"].date().isoformat(),
        "description": str(row["description"]),
        "amount": str(row["amount"]),
        "type": str(row["type"]),
        "category": str(row["category"]),
        "provider": str(row["provider"]),
        "payment_method": str(row["payment_method"]),
    }


def preview_bank_csv(db: Session, content: bytes, sample_limit: int = 10) -> dict[str, int | list[str] | list[dict[str, str]]]:
    try:
        rows = _parse_csv_content(content)
    except Exception as exc:  # noqa: BLE001
        return {
            "total_rows": 0,
            "importable": 0,
            "duplicates": 0,
            "errors": [str(exc)],
            "sample_rows": [],
        }

    importable = 0
    duplicates = 0
    sample_rows: list[dict[str, str]] = []

    for row in rows:
        is_duplicate = find_duplicate(db, str(row["provider"]), str(row["external_id"])) is not None
        status = "duplicate" if is_duplicate else "ready"
        if is_duplicate:
            duplicates += 1
        else:
            importable += 1
        if len(sample_rows) < sample_limit:
            sample_rows.append(_preview_row(row, status))

    return {
        "total_rows": len(rows),
        "importable": importable,
        "duplicates": duplicates,
        "errors": [],
        "sample_rows": sample_rows,
    }


def preview_bank_ofx(db: Session, content: bytes, sample_limit: int = 10) -> dict[str, int | list[str] | list[dict[str, str]]]:
    try:
        rows = parse_ofx(content)
    except Exception as exc:
        return {"total_rows": 0, "importable": 0, "duplicates": 0, "errors": [str(exc)], "sample_rows": []}

    importable = 0
    duplicates = 0
    sample_rows: list[dict[str, str]] = []

    for row in rows:
        is_duplicate = find_duplicate(db, str(row["provider"]), str(row["external_id"])) is not None
        status = "duplicate" if is_duplicate else "ready"
        if is_duplicate:
            duplicates += 1
        else:
            importable += 1
        if len(sample_rows) < sample_limit:
            sample_rows.append(_preview_row(row, status))

    return {"total_rows": len(rows), "importable": importable, "duplicates": duplicates, "errors": [], "sample_rows": sample_rows}


def import_bank_ofx(db: Session, content: bytes) -> dict[str, int | list[str]]:
    try:
        rows = parse_ofx(content)
    except Exception as exc:
        return {"total_rows": 0, "imported": 0, "ignored": 0, "errors": [str(exc)]}

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
            )
            create_transaction(db, payload)
            imported += 1
        except ValueError:
            ignored += 1
        except Exception as exc:
            ignored += 1
            errors.append(f"Transação {index}: {exc}")

    return {"total_rows": len(rows), "imported": imported, "ignored": ignored, "errors": errors}


def import_bank_csv(db: Session, content: bytes, force_provider: str | None = None) -> dict[str, int | list[str]]:
    rows = _parse_csv_content(content)
    imported = 0
    ignored = 0
    errors: list[str] = []

    for index, row in enumerate(rows, start=1):
        try:
            provider = force_provider or str(row["provider"])
            payload = TransactionCreate(
                external_id=str(row["external_id"]),
                provider=provider,
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
        except Exception as exc:  # noqa: BLE001
            ignored += 1
            errors.append(f"Linha {index}: {exc}")

    return {
        "total_rows": len(rows),
        "imported": imported,
        "ignored": ignored,
        "errors": errors,
    }
