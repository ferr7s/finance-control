from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.credit_card import CreditCard
from app.models.credit_card_bill import CreditCardBill
from app.models.transaction import Transaction
from app.schemas.dashboard import (
    CategoryBreakdownItem,
    CreditCardSummaryItem,
    DashboardSummary,
    MonthlyCashflowPoint,
    RecurringExpenseItem,
)
from app.utils.dates import month_bounds


UNPAID_BILL_STATUSES = {"open", "closed", "overdue", "unknown"}


def get_accounts_balance(db: Session) -> Decimal:
    return db.scalar(select(func.coalesce(func.sum(Account.current_balance), 0))) or Decimal("0.00")


def get_open_bills_total(db: Session) -> Decimal:
    stmt = select(func.coalesce(func.sum(CreditCardBill.amount), 0)).where(CreditCardBill.status.in_(UNPAID_BILL_STATUSES))
    return db.scalar(stmt) or Decimal("0.00")


def get_net_worth(db: Session) -> dict[str, Decimal]:
    accounts_balance = get_accounts_balance(db)
    open_bills_total = get_open_bills_total(db)
    return {
        "accounts_balance": accounts_balance,
        "open_bills_total": open_bills_total,
        "net_worth": accounts_balance - open_bills_total,
    }


def get_dashboard_summary(db: Session) -> DashboardSummary:
    start, end = month_bounds()
    monthly_income = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.date >= start,
            Transaction.date < end,
            Transaction.type == "income",
        )
    ) or Decimal("0.00")
    monthly_expenses = db.scalar(
        select(func.coalesce(func.sum(func.abs(Transaction.amount)), 0)).where(
            Transaction.date >= start,
            Transaction.date < end,
            Transaction.type.in_(["expense", "credit_card"]),
        )
    ) or Decimal("0.00")
    net = get_net_worth(db)
    recurring = get_recurring_expenses(db)
    recurring_total = sum((item.amount for item in recurring), Decimal("0.00"))
    estimated_available = net["accounts_balance"] + monthly_income - recurring_total - net["open_bills_total"]
    warnings = []
    if not recurring:
        warnings.append("Dados insuficientes para estimar recorrências com alta confiança.")
    return DashboardSummary(
        net_worth=net["net_worth"],
        accounts_balance=net["accounts_balance"],
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_result=monthly_income - monthly_expenses,
        open_bills_total=net["open_bills_total"],
        estimated_available=estimated_available,
        warnings=warnings,
    )


def get_monthly_cashflow(db: Session) -> list[MonthlyCashflowPoint]:
    rows = db.execute(
        select(
            extract("year", Transaction.date).label("year"),
            extract("month", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount),
        )
        .group_by("year", "month", Transaction.type)
        .order_by("year", "month")
    ).all()
    grouped: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"income": Decimal("0.00"), "expenses": Decimal("0.00")})
    for year, month, tx_type, total in rows:
        key = f"{int(year):04d}-{int(month):02d}"
        if tx_type == "income":
            grouped[key]["income"] += total or Decimal("0.00")
        elif tx_type in {"expense", "credit_card"}:
            grouped[key]["expenses"] += abs(total or Decimal("0.00"))
    return [
        MonthlyCashflowPoint(
            month=month,
            income=values["income"],
            expenses=values["expenses"],
            result=values["income"] - values["expenses"],
        )
        for month, values in grouped.items()
    ]


def get_category_breakdown(db: Session) -> list[CategoryBreakdownItem]:
    start, end = month_bounds()
    rows = db.execute(
        select(Transaction.category, func.sum(func.abs(Transaction.amount)))
        .where(Transaction.date >= start, Transaction.date < end, Transaction.type.in_(["expense", "credit_card"]))
        .group_by(Transaction.category)
        .order_by(func.sum(func.abs(Transaction.amount)).desc())
    ).all()
    total = sum((amount or Decimal("0.00") for _, amount in rows), Decimal("0.00"))
    if total == 0:
        return []
    return [
        CategoryBreakdownItem(
            category=category or "outros",
            amount=amount or Decimal("0.00"),
            percentage=float(((amount or Decimal("0.00")) / total) * 100),
        )
        for category, amount in rows
    ]


def get_recurring_expenses(db: Session) -> list[RecurringExpenseItem]:
    rows = db.execute(
        select(Transaction.description, Transaction.category, func.avg(func.abs(Transaction.amount)), func.count(Transaction.id))
        .where(Transaction.type.in_(["expense", "credit_card"]))
        .group_by(Transaction.description, Transaction.category)
        .having(func.count(Transaction.id) >= 3)
        .order_by(func.count(Transaction.id).desc())
    ).all()
    return [
        RecurringExpenseItem(
            description=description,
            category=category,
            amount=Decimal(avg_amount).quantize(Decimal("0.01")),
            occurrences=count,
        )
        for description, category, avg_amount, count in rows
    ]


def get_credit_card_summary(db: Session) -> list[CreditCardSummaryItem]:
    cards = db.scalars(select(CreditCard).order_by(CreditCard.name)).all()
    result: list[CreditCardSummaryItem] = []
    for card in cards:
        open_amount = db.scalar(
            select(func.coalesce(func.sum(CreditCardBill.amount), 0)).where(
                CreditCardBill.credit_card_id == card.id,
                CreditCardBill.status.in_(UNPAID_BILL_STATUSES),
            )
        ) or Decimal("0.00")
        result.append(
            CreditCardSummaryItem(
                id=str(card.id),
                name=card.name,
                provider=card.provider,
                limit_total=card.limit_total,
                limit_available=card.limit_available,
                open_bill_amount=open_amount,
                due_day=card.due_day,
                closing_day=card.closing_day,
            )
        )
    return result


def get_largest_expenses(db: Session, limit: int = 8) -> list[dict]:
    start, end = month_bounds()
    rows = db.scalars(
        select(Transaction)
        .where(Transaction.date >= start, Transaction.date < end, Transaction.type.in_(["expense", "credit_card"]))
        .order_by(func.abs(Transaction.amount).desc())
        .limit(limit)
    ).all()
    return [
        {
            "date": tx.date.isoformat(),
            "description": tx.description,
            "amount": str(abs(tx.amount)),
            "category": tx.category,
            "provider": tx.provider,
        }
        for tx in rows
    ]


def analyzed_period_label() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"
