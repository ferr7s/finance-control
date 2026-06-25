from decimal import Decimal
from unicodedata import normalize

from app.utils.money import parse_money


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "alimentação": (
        "ifood", "rappi", "ze delivery", "zé delivery", "restaurante", "lanchonete",
        "padaria", "panificadora", "mercado", "supermercado", "hipermercado",
        "atacadao", "atacadão", "carrefour", "assai", "assaí", "extra", "pao de acucar",
        "pão de açúcar", "hortifruti", "sacolao", "sacolão", "feira", "acougue", "açougue",
        "peixaria", "sushi", "pizza", "hamburger", "hamburguer", "burguer", "burger",
        "mcdonalds", "mcdonald", "subway", "outback", "habibs", "habib", "giraffas",
        "bob's", "bobs", "coxinha", "pastel", "delivery", "almoco", "almoço", "jantar",
        "cafe", "cafeteria", "sorveteria", "doceria",
    ),
    "transporte": (
        "uber", "99", "cabify", "metro", "metrô", "onibus", "ônibus", "taxi", "táxi",
        "gasolina", "combustivel", "combustível", "etanol", "diesel",
        "posto", "shell", "petrobras", "ipiranga", "br distribuidora",
        "estacionamento", "pedagio", "pedágio", "autopass", "sem parar", "veloe",
        "ipva", "dpvat", "licenciamento", "detran", "oficina", "mecanico", "mecânico",
        "pneu", "borracharia",
    ),
    "saúde": (
        "farmacia", "farmácia", "drogasil", "droga raia", "ultrafarma", "pacheco",
        "extrafarma", "nissei", "pague menos", "panvel",
        "academia", "smartfit", "bluefit", "bodytech",
        "medico", "médico", "consulta", "clinica", "clínica", "hospital",
        "laboratorio", "laboratório", "exame", "dentista", "odonto",
        "psicologo", "psicólogo", "psiquiatra", "terapia",
        "plano de saude", "plano de saúde", "unimed", "hapvida", "amil", "sulamerica",
        "bradesco saude", "bradesco saúde", "sulamérica",
    ),
    "assinaturas": (
        "netflix", "spotify", "prime video", "amazon prime", "hbo", "hbo max",
        "disney", "disney+", "paramount", "globoplay", "telecine", "mubi",
        "youtube premium", "apple", "apple tv", "icloud",
        "adobe", "microsoft", "office", "dropbox", "notion",
        "chatgpt", "openai", "canva", "figma",
        "deezer", "tidal", "amazon music",
        "antivirus", "kaspersky", "norton", "eset",
    ),
    "moradia": (
        "aluguel", "condominio", "condomínio", "iptu",
        "luz", "energia", "enel", "cemig", "copel", "celpe", "eletropaulo",
        "agua", "água", "saneamento", "sabesp", "caesb", "compesa",
        "gas", "gás", "comgas", "cegás",
        "internet", "vivo", "claro", "tim", "oi", "net", "sky", "algar",
        "telefone", "celular",
        "limpeza", "portaria", "seguro residencial", "mudança",
    ),
    "educação": (
        "mensalidade", "escola", "colegio", "colégio", "faculdade", "universidade",
        "curso", "aula", "treinamento", "capacitacao", "capacitação",
        "udemy", "alura", "coursera", "hotmart", "kiwify", "eduzz",
        "livro", "livraria", "saraiva", "amazon livro", "cultura",
        "papelaria", "kalunga", "staples", "campus", "vestibular",
    ),
    "vestuário": (
        "renner", "c&a", "cea", "zara", "hering", "riachuelo", "marisa",
        "shein", "dafiti", "netshoes", "centauro",
        "nike", "adidas", "puma", "fila", "asics", "mizuno",
        "arezzo", "carmen steffens", "schutz", "havaianas", "ipanema",
        "roupa", "calçado", "calcado", "tenis", "tênis", "sapato", "sandalia", "sandália",
    ),
    "beleza": (
        "salao", "salão", "cabeleireiro", "barbearia", "barber",
        "manicure", "pedicure", "estetica", "estética", "depilacao", "depilação",
        "perfume", "sephora", "o boticario", "o boticário", "natura", "avon",
        "loreal", "l'oreal", "nars", "mac cosmeticos",
    ),
    "pets": (
        "petshop", "pet shop", "cobasi", "petz", "petlove",
        "veterinario", "veterinário", "clinica vet", "ração", "racao",
        "banho e tosa", "dog", "gato", "animal",
    ),
    "lazer": (
        "cinema", "cine", "ingresso", "ingresso.com", "sympla", "eventbrite",
        "show", "festival", "teatro", "museu",
        "bar", "balada", "boate", "pub", "choperia",
        "hotel", "pousada", "airbnb", "booking", "hotel.com",
        "viagem", "passagem", "latam", "gol", "azul", "tam",
        "cruzeiro", "resort",
        "steam", "playstation", "xbox", "nintendo", "epic games",
        "clube", "golfe", "futebol", "natacao", "natação",
    ),
    "renda": (
        "salario", "salário", "pagamento", "pix recebido", "deposito recebido",
        "transferencia recebida", "transferência recebida",
        "13 salario", "13 salário", "ferias", "férias", "bonus", "bônus",
        "dividendo", "dividendo", "juros recebido",
        "freelance", "honorario", "honorário",
    ),
    "investimentos": (
        "corretora", "xp investimentos", "rico", "clear", "easynvest", "nu invest",
        "investimento", "aporte", "aplicacao", "aplicação",
        "cdb", "lci", "lca", "tesouro direto", "fundo", "acao", "ação",
        "btc", "bitcoin", "cripto", "binance", "coinbase",
    ),
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
