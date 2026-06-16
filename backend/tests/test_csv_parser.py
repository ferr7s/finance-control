from io import StringIO

from app.utils.csv_parser import parse_bank_csv


def test_parse_bank_csv_accepts_semicolon_and_brazilian_columns():
    content = "data;descrição;valor;banco\n01/06/2026;iFood;-45,90;Nubank\n"

    rows = parse_bank_csv(StringIO(content))

    assert len(rows) == 1
    assert rows[0]["date"].isoformat() == "2026-06-01T00:00:00"
    assert rows[0]["description"] == "iFood"
    assert str(rows[0]["amount"]) == "-45.90"
    assert rows[0]["provider"] == "Nubank"


def test_parse_bank_csv_generates_stable_external_id_for_deduplication():
    content = "data;descrição;valor;banco\n01/06/2026;iFood;-45,90;Nubank\n"

    first = parse_bank_csv(StringIO(content))
    second = parse_bank_csv(StringIO(content))

    assert first[0]["external_id"].startswith("csv:")
    assert first[0]["external_id"] == second[0]["external_id"]
