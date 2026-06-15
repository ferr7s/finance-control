from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insight import Insight
from app.schemas.insight import InsightCreate
from app.services.dashboard_service import get_category_breakdown, get_credit_card_summary, get_recurring_expenses


def list_insights(db: Session) -> list[Insight]:
    return list(db.scalars(select(Insight).order_by(Insight.created_at.desc())).all())


def create_insight(db: Session, payload: InsightCreate) -> Insight:
    insight = Insight(**payload.model_dump())
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight


def generate_insights(db: Session) -> list[Insight]:
    generated: list[InsightCreate] = []
    recurring = get_recurring_expenses(db)
    if recurring:
        generated.append(
            InsightCreate(
                type="recurring",
                title="Gastos recorrentes detectados",
                content=f"Foram encontrados {len(recurring)} gastos recorrentes com base no histórico importado.",
                severity="info",
            )
        )

    categories = get_category_breakdown(db)
    if categories:
        top = categories[0]
        severity = "warning" if top.amount > Decimal("1000.00") else "info"
        generated.append(
            InsightCreate(
                type="category_spike",
                title=f"Categoria em destaque: {top.category}",
                content=f"{top.category} representa {top.percentage:.1f}% dos gastos do mês.",
                severity=severity,
            )
        )

    cards = get_credit_card_summary(db)
    high_cards = [card for card in cards if card.open_bill_amount > Decimal("1500.00")]
    if high_cards:
        generated.append(
            InsightCreate(
                type="credit_card",
                title="Fatura atual acima da média esperada",
                content="Há faturas abertas com valor relevante. Revise o impacto no disponível estimado.",
                severity="warning",
            )
        )

    if not generated:
        generated.append(
            InsightCreate(
                type="data_quality",
                title="Dados ainda insuficientes",
                content="Importe mais transações para gerar insights determinísticos mais úteis.",
                severity="info",
            )
        )

    saved = [create_insight(db, item) for item in generated]
    return saved
