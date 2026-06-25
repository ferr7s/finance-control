import csv
import hashlib
from decimal import Decimal
from datetime import datetime
from typing import TextIO

from app.utils.categorizer import categorize_transaction, infer_transaction_type
from app.utils.dates import parse_date
from app.utils.money import parse_money


COLUMN_ALIASES = {
    "date": {"date", "data"},
    "description": {"description", "descricao", "descrição", "historico", "histórico", "movimentacao", "movimentação"},
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


def _normalize_external_id_part(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def build_csv_external_id(provider: str, date: datetime, description: str, amount: Decimal) -> str:
    fingerprint = "|".join(
        [
            "bank-csv",
            _normalize_external_id_part(provider),
            date.date().isoformat(),
            _normalize_external_id_part(description),
            str(amount.quantize(Decimal("0.01"))),
        ]
    )
    return f"csv:{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()[:24]}"


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
        date = parse_date(str(raw.get("date") or ""))
        provider = str(raw.get("provider") or "csv").strip() or "csv"
        rows.append(
            {
                "external_id": build_csv_external_id(provider, date, description, amount),
                "date": date,
                "description": description,
                "amount": amount,
                "type": infer_transaction_type(amount, description, str(explicit_type) if explicit_type else None),
                "category": category,
                "provider": provider,
                "account": str(raw.get("account") or "").strip() or None,
                "card": str(raw.get("card") or "").strip() or None,
                "payment_method": "credit" if raw.get("card") else "unknown",
            }
        )
    return rows


def are_amounts_close(left: Decimal, right: Decimal, tolerance: Decimal = Decimal("1.00")) -> bool:
    return abs(left - right) <= tolerance
