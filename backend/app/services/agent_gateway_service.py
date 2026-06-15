from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.schemas.agent_analysis import AgentAnalysisCreate
from app.schemas.dashboard import FinancialContext
from app.schemas.transaction import TransactionSearchRequest
from app.services import dashboard_service
from app.services.agent_analyses_service import create_agent_analysis
from app.services.transactions_service import search_transactions


SAFETY_INSTRUCTIONS = [
    "Não inventar dados.",
    "Avisar quando não houver dados suficientes.",
    "Focar em organização financeira, hábitos, orçamento e planejamento.",
    "Não dar recomendação específica de investimento.",
    "Não sugerir ações financeiras automáticas.",
    "Não pedir senhas bancárias.",
    "Não pedir seed phrase ou chaves privadas.",
    "Não executar pagamentos, Pix ou transferências.",
]


def generate_financial_context(db: Session) -> FinancialContext:
    summary = dashboard_service.get_dashboard_summary(db)
    categories = dashboard_service.get_category_breakdown(db)
    recurring = dashboard_service.get_recurring_expenses(db)
    cards = dashboard_service.get_credit_card_summary(db)
    largest = dashboard_service.get_largest_expenses(db)
    net = dashboard_service.get_net_worth(db)
    insufficient_data = []
    if not categories:
        insufficient_data.append("Sem gastos categorizados suficientes no mês atual.")
    if not recurring:
        insufficient_data.append("Sem histórico suficiente para detectar recorrências com confiança.")

    return FinancialContext(
        analyzed_period=dashboard_service.analyzed_period_label(),
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        bank_net_worth=net["net_worth"],
        accounts_balance=net["accounts_balance"],
        open_bills_total=net["open_bills_total"],
        monthly_income=summary.monthly_income,
        monthly_expenses=summary.monthly_expenses,
        monthly_result=summary.monthly_result,
        estimated_available_until_month_end=summary.estimated_available,
        category_breakdown=categories,
        largest_expenses=largest,
        recurring_expenses=recurring,
        credit_cards=cards,
        alerts=summary.warnings,
        insufficient_data=insufficient_data,
        useful_questions=[
            "Quais categorias cresceram mais neste mês?",
            "Quais recorrências podem ser renegociadas ou canceladas?",
            "O disponível estimado cobre faturas e gastos recorrentes até o fim do mês?",
        ],
        safety_instructions=SAFETY_INSTRUCTIONS,
    )


def search_agent_transactions(db: Session, payload: TransactionSearchRequest):
    return search_transactions(db, payload)


def save_agent_analysis(db: Session, payload: AgentAnalysisCreate):
    return create_agent_analysis(db, payload)
