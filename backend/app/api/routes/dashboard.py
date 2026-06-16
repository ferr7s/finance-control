from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import (
    CategoryBreakdownItem,
    CreditCardSummaryItem,
    DashboardSummary,
    LargestExpenseItem,
    MonthlyCashflowPoint,
    RecurringExpenseItem,
)
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_summary(db)


@router.get("/monthly-cashflow", response_model=list[MonthlyCashflowPoint])
def monthly_cashflow(db: Session = Depends(get_db)):
    return dashboard_service.get_monthly_cashflow(db)


@router.get("/category-breakdown", response_model=list[CategoryBreakdownItem])
def category_breakdown(db: Session = Depends(get_db)):
    return dashboard_service.get_category_breakdown(db)


@router.get("/net-worth")
def net_worth(db: Session = Depends(get_db)):
    return dashboard_service.get_net_worth(db)


@router.get("/recurring-expenses", response_model=list[RecurringExpenseItem])
def recurring_expenses(db: Session = Depends(get_db)):
    return dashboard_service.get_recurring_expenses(db)


@router.get("/credit-card-summary", response_model=list[CreditCardSummaryItem])
def credit_card_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_credit_card_summary(db)


@router.get("/largest-expenses", response_model=list[LargestExpenseItem])
def largest_expenses(db: Session = Depends(get_db)):
    return dashboard_service.get_largest_expenses(db)
