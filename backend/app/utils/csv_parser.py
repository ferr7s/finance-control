import csv
from decimal import Decimal
from typing import TextIO

from app.utils.categorizer import categorize_transaction, infer_transaction_type
from app.utils.dates import parse_date
from app.utils.money import parse_money


COLUMN_ALIASES = {
    "date": {"date", "data"},
    "description": {"description", "descricao", "descrição", "historico", "histórico"},
    "amount": {"amount", "valor"},
    "type": {"type", "tipo"},
    "category": {"category", "categoria"},
    "account": {"account", "conta"},
    "card": {"card", "cartão", "cartao"},
    "provider": {"provider", "banco", "instituição", "instituicao"},
}


def _detect_dialect(sample: str) -> csv.Dialect:
    return csv.Sniffer().sniff(sample, delimiters=",;")


def _canonical_header(header: str) -> str:
    normalized = header.strip().lower()
    for canonical, aliases in COLUMN_ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized


def parse_bank_csv(file_obj: TextIO) -> list[dict[str, object]]:
    sample = file_obj.read(4096)
    file_obj.seek(0)
    dialect = _detect_dialect(sample)
    reader = csv.DictReader(file_obj, dialect=dialect)
    if not reader.fieldnames:
        return []

    reader.fieldnames = [_canonical_header(field) for field in reader.fieldnames]
    rows: list[dict[str, object]] = []
    for raw in reader:
        description = str(raw.get("description") or "").strip()
        amount = parse_money(str(raw.get("amount") or "0"))
        explicit_type = raw.get("type")
        category = str(raw.get("category") or "").strip() or categorize_transaction(description)
        rows.append(
            {
                "date": parse_date(str(raw.get("date") or "")),
                "description": description,
                "amount": amount,
                "type": infer_transaction_type(amount, description, str(explicit_type) if explicit_type else None),
                "category": category,
                "provider": str(raw.get("provider") or "csv").strip() or "csv",
                "account": str(raw.get("account") or "").strip() or None,
                "card": str(raw.get("card") or "").strip() or None,
                "payment_method": "credit" if raw.get("card") else "unknown",
            }
        )
    return rows


def are_amounts_close(left: Decimal, right: Decimal, tolerance: Decimal = Decimal("1.00")) -> bool:
    return abs(left - right) <= tolerance
