from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_agent_api_key
from app.schemas.agent_analysis import AgentAnalysisCreate, AgentAnalysisRead
from app.schemas.dashboard import CategoryBreakdownItem, CreditCardSummaryItem, DashboardSummary, FinancialContext, MonthlyCashflowPoint, RecurringExpenseItem
from app.schemas.transaction import TransactionRead, TransactionSearchRequest
from app.services import agent_gateway_service, dashboard_service

router = APIRouter(prefix="/api/agent", tags=["agent"], dependencies=[Depends(require_agent_api_key)])


@router.get("/health")
def agent_health() -> dict[str, str | bool]:
    return {"status": "ok", "read_only": True}


@router.get("/dashboard-summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_summary(db)


@router.get("/net-worth")
def net_worth(db: Session = Depends(get_db)):
    return dashboard_service.get_net_worth(db)


@router.get("/category-breakdown", response_model=list[CategoryBreakdownItem])
def category_breakdown(db: Session = Depends(get_db)):
    return dashboard_service.get_category_breakdown(db)


@router.get("/monthly-cashflow", response_model=list[MonthlyCashflowPoint])
def monthly_cashflow(db: Session = Depends(get_db)):
    return dashboard_service.get_monthly_cashflow(db)


@router.get("/recurring-expenses", response_model=list[RecurringExpenseItem])
def recurring_expenses(db: Session = Depends(get_db)):
    return dashboard_service.get_recurring_expenses(db)


@router.get("/credit-card-summary", response_model=list[CreditCardSummaryItem])
def credit_card_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_credit_card_summary(db)


@router.post("/transactions/search", response_model=list[TransactionRead])
def search_transactions(payload: TransactionSearchRequest, db: Session = Depends(get_db)):
    return agent_gateway_service.search_agent_transactions(db, payload)


@router.post("/context/generate", response_model=FinancialContext)
def generate_context(db: Session = Depends(get_db)):
    return agent_gateway_service.generate_financial_context(db)


@router.post("/analyses", response_model=AgentAnalysisRead)
def save_analysis(payload: AgentAnalysisCreate, db: Session = Depends(get_db)):
    return agent_gateway_service.save_agent_analysis(db, payload)
