from decimal import Decimal
from unicodedata import normalize

from app.utils.money import parse_money


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "alimentação": ("ifood", "restaurante", "mercado", "padaria"),
    "transporte": ("uber", "99", "metro", "metrô", "gasolina"),
    "saúde": ("academia", "farmacia", "farmácia", "medico", "médico"),
    "assinaturas": ("netflix", "spotify", "prime", "hbo"),
    "moradia": ("aluguel", "condominio", "condomínio", "luz", "agua", "água", "internet"),
    "renda": ("salario", "salário", "pagamento", "pix recebido"),
    "investimentos": ("corretora", "investimento", "aporte"),
    "lazer": ("cinema", "bar", "ingresso", "show"),
}


def _fold(text: str) -> str:
    return normalize("NFKD", text.lower()).encode("ascii", "ignore").decode("ascii")


def categorize_transaction(description: str, fallback: str | None = None) -> str:
    folded = _fold(description)
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(_fold(keyword) in folded for keyword in keywords):
            return category
    return fallback or "outros"


def infer_transaction_type(amount: Decimal | str, description: str = "", explicit_type: str | None = None) -> str:
    if explicit_type:
        normalized_type = _fold(explicit_type).replace(" ", "_")
        if normalized_type in {"income", "expense", "transfer", "credit_card"}:
            return normalized_type

    folded = _fold(description)
    if "transfer" in folded or "pix enviado" in folded:
        return "transfer"

    value = amount if isinstance(amount, Decimal) else parse_money(str(amount))
    return "income" if value >= Decimal("0") else "expense"
