from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.account import Account
from app.models.agent_analysis import AgentAnalysis
from app.models.credit_card import CreditCard
from app.models.credit_card_bill import CreditCardBill
from app.models.insight import Insight
from app.models.transaction import Transaction
from app.utils.categorizer import categorize_transaction, infer_transaction_type


def month_start(reference: date, offset: int) -> date:
    month = reference.month + offset
    year = reference.year
    while month <= 0:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return date(year, month, 1)


def add_transaction(
    db,
    *,
    provider: str,
    description: str,
    amount: Decimal,
    day: date,
    account_id=None,
    credit_card_id=None,
    bill_id=None,
    external_id: str,
    payment_method: str = "unknown",
    category: str | None = None,
):
    exists = db.scalar(select(Transaction).where(Transaction.provider == provider, Transaction.external_id == external_id))
    if exists:
        return exists
    tx_type = "credit_card" if credit_card_id else infer_transaction_type(amount, description)
    tx = Transaction(
        provider=provider,
        external_id=external_id,
        account_id=account_id,
        credit_card_id=credit_card_id,
        bill_id=bill_id,
        date=datetime(day.year, day.month, day.day),
        description=description,
        amount=amount,
        type=tx_type,
        payment_method=payment_method,
        category=category or categorize_transaction(description),
        merchant=description.split()[0],
        is_recurring=description in {"Netflix", "Spotify", "Academia", "Aluguel", "Internet Fibra"},
        raw_data={"seed": True},
    )
    db.add(tx)
    return tx


def run() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(Account.id).limit(1)):
            print("Seed already present; skipping.")
            return

        nubank_account = Account(
            provider="nubank",
            name="Nubank Conta",
            type="payment_account",
            current_balance=Decimal("8420.55"),
            institution_name="Nubank",
            account_number_masked="**** 1020",
        )
        itau_account = Account(
            provider="itau",
            name="Itaú Conta",
            type="checking",
            current_balance=Decimal("12650.30"),
            institution_name="Itaú",
            branch="1234",
            account_number_masked="**** 7788",
        )
        db.add_all([nubank_account, itau_account])
        db.flush()

        nubank_card = CreditCard(
            provider="nubank",
            name="Nubank Cartão",
            brand="Mastercard",
            limit_total=Decimal("12000.00"),
            limit_available=Decimal("7350.00"),
            closing_day=20,
            due_day=27,
        )
        itau_card = CreditCard(
            provider="itau",
            name="Itaú Cartão",
            brand="Visa",
            limit_total=Decimal("18000.00"),
            limit_available=Decimal("12200.00"),
            closing_day=15,
            due_day=22,
        )
        db.add_all([nubank_card, itau_card])
        db.flush()

        today = date.today()
        bills_by_key = {}
        for offset, status in [(-3, "paid"), (-2, "paid"), (-1, "closed"), (0, "open")]:
            ref = month_start(today, offset)
            for card, base_amount in [(nubank_card, Decimal("2450.00")), (itau_card, Decimal("1780.00"))]:
                amount = base_amount + Decimal(abs(offset) * 180)
                bill = CreditCardBill(
                    credit_card_id=card.id,
                    reference_month=ref,
                    due_date=date(ref.year, ref.month, min(card.due_day or 20, 28)),
                    closing_date=date(ref.year, ref.month, min(card.closing_day or 15, 28)),
                    amount=amount,
                    status=status,
                )
                db.add(bill)
                db.flush()
                bills_by_key[(card.name, ref.isoformat())] = bill

        recurring = [
            ("Aluguel", Decimal("-2800.00"), itau_account.id, None, "transfer"),
            ("Internet Fibra", Decimal("-129.90"), nubank_account.id, None, "debit"),
            ("Netflix", Decimal("-55.90"), None, nubank_card.id, "credit"),
            ("Spotify", Decimal("-21.90"), None, nubank_card.id, "credit"),
            ("Academia", Decimal("-119.90"), None, itau_card.id, "credit"),
        ]
        variable = [
            ("Mercado Zona Sul", Decimal("-382.44"), nubank_account.id, None, "debit"),
            ("iFood Restaurante", Decimal("-68.70"), None, nubank_card.id, "credit"),
            ("Uber Viagem", Decimal("-32.10"), None, nubank_card.id, "credit"),
            ("Farmácia", Decimal("-96.40"), itau_account.id, None, "debit"),
            ("Cinema ingresso", Decimal("-84.00"), None, itau_card.id, "credit"),
            ("Bar com amigos", Decimal("-132.00"), None, itau_card.id, "credit"),
            ("Investimento corretora", Decimal("-750.00"), itau_account.id, None, "transfer"),
            ("Padaria", Decimal("-28.50"), nubank_account.id, None, "debit"),
            ("Luz", Decimal("-210.30"), itau_account.id, None, "boleto"),
            ("Água", Decimal("-92.15"), itau_account.id, None, "boleto"),
            ("Pix enviado", Decimal("-120.00"), nubank_account.id, None, "pix"),
        ]

        counter = 0
        for offset in range(-3, 1):
            ref = month_start(today, offset)
            payday = date(ref.year, ref.month, min(5, 28))
            add_transaction(
                db,
                provider="itau",
                description="Salário",
                amount=Decimal("9800.00"),
                day=payday,
                account_id=itau_account.id,
                external_id=f"seed-salary-{ref.isoformat()}",
                payment_method="transfer",
                category="renda",
            )
            add_transaction(
                db,
                provider="nubank",
                description="Pix recebido projeto",
                amount=Decimal("1250.00"),
                day=date(ref.year, ref.month, min(12, 28)),
                account_id=nubank_account.id,
                external_id=f"seed-pix-income-{ref.isoformat()}",
                payment_method="pix",
                category="renda",
            )
            for index, (description, amount, account_id, card_id, method) in enumerate(recurring):
                card = nubank_card if card_id == nubank_card.id else itau_card if card_id == itau_card.id else None
                bill = bills_by_key.get((card.name, ref.isoformat())) if card else None
                add_transaction(
                    db,
                    provider="nubank" if card_id == nubank_card.id or account_id == nubank_account.id else "itau",
                    description=description,
                    amount=amount,
                    day=date(ref.year, ref.month, min(7 + index * 3, 28)),
                    account_id=account_id,
                    credit_card_id=card_id,
                    bill_id=bill.id if bill else None,
                    external_id=f"seed-recurring-{offset}-{index}",
                    payment_method=method,
                )
                counter += 1
            for index, (description, amount, account_id, card_id, method) in enumerate(variable):
                for repeat in range(2):
                    varied = amount - Decimal(index * repeat * 3)
                    card = nubank_card if card_id == nubank_card.id else itau_card if card_id == itau_card.id else None
                    bill = bills_by_key.get((card.name, ref.isoformat())) if card else None
                    add_transaction(
                        db,
                        provider="nubank" if card_id == nubank_card.id or account_id == nubank_account.id else "itau",
                        description=description,
                        amount=varied,
                        day=date(ref.year, ref.month, min(3 + index + repeat * 12, 28)),
                        account_id=account_id,
                        credit_card_id=card_id,
                        bill_id=bill.id if bill else None,
                        external_id=f"seed-variable-{offset}-{index}-{repeat}",
                        payment_method=method,
                    )
                    counter += 1

        db.add_all(
            [
                Insight(
                    type="recurring",
                    title="Gasto recorrente detectado",
                    content="Netflix, Spotify, academia, aluguel e internet aparecem de forma consistente no histórico.",
                    severity="info",
                ),
                Insight(
                    type="category_spike",
                    title="Alimentação acima do mês anterior",
                    content="Mercado, iFood e padaria estão concentrando parte relevante dos gastos variáveis.",
                    severity="warning",
                ),
                Insight(
                    type="saving",
                    title="Possível economia com assinaturas",
                    content="Revise assinaturas recorrentes antes do fechamento da próxima fatura.",
                    severity="success",
                ),
                Insight(
                    type="credit_card",
                    title="Fatura atual acima da média",
                    content="A fatura aberta do cartão Nubank está acima dos meses pagos do seed.",
                    severity="warning",
                ),
            ]
        )
        db.add_all(
            [
                AgentAnalysis(
                    source="hermes",
                    title="Análise automática sobre gastos do mês",
                    content="O mês está saudável, mas alimentação e transporte merecem acompanhamento semanal.",
                    metadata_json={"period": "current_month", "confidence": "seed"},
                ),
                AgentAnalysis(
                    source="hermes",
                    title="Análise automática sobre fatura",
                    content="A fatura aberta concentra assinaturas e lazer. Não há ação financeira recomendada automaticamente.",
                    metadata_json={"surface": "credit_card"},
                ),
                AgentAnalysis(
                    source="hermes",
                    title="Análise automática sobre recorrências",
                    content="Foram detectados gastos recorrentes suficientes para apoiar um orçamento mensal determinístico.",
                    metadata_json={"recurrences": ["Netflix", "Spotify", "Academia", "Aluguel"]},
                ),
            ]
        )
        db.commit()
        print(f"Seed completed with {counter + 8} transactions.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
