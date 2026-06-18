from app.services import import_service
from app.utils.csv_parser import parse_bank_csv


def test_preview_bank_csv_reports_importable_and_duplicate_rows(monkeypatch):
    content = (
        "data;descricao;valor;banco\n"
        "01/06/2026;iFood;-45,90;Nubank\n"
        "02/06/2026;Mercado;-120,30;Nubank\n"
    )
    duplicate_external_id = parse_bank_csv_from_text(content)[0]["external_id"]

    def fake_find_duplicate(db, provider, external_id):
        return object() if external_id == duplicate_external_id else None

    monkeypatch.setattr(import_service, "find_duplicate", fake_find_duplicate)

    preview = import_service.preview_bank_csv(db=object(), content=content.encode())

    assert preview["total_rows"] == 2
    assert preview["importable"] == 1
    assert preview["duplicates"] == 1
    assert preview["errors"] == []
    assert [row["status"] for row in preview["sample_rows"]] == ["duplicate", "ready"]
    assert preview["sample_rows"][0]["description"] == "iFood"
    assert preview["sample_rows"][1]["description"] == "Mercado"


def parse_bank_csv_from_text(content: str):
    from io import StringIO

    return parse_bank_csv(StringIO(content))
