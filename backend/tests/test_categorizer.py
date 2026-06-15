from app.utils.categorizer import categorize_transaction, infer_transaction_type


def test_categorizes_known_merchants_by_keywords():
    assert categorize_transaction("Compra iFood restaurante") == "alimentação"
    assert categorize_transaction("Uber viagem") == "transporte"
    assert categorize_transaction("Netflix assinatura mensal") == "assinaturas"


def test_infers_type_from_amount_when_not_transfer():
    assert infer_transaction_type("1200.00", "Pix recebido") == "income"
    assert infer_transaction_type("-45.00", "Mercado") == "expense"
    assert infer_transaction_type("-100.00", "Transferencia entre contas") == "transfer"
