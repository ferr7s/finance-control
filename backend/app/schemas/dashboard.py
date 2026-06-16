from decimal import Decimal

from pydantic import BaseModel


class MetricPoint(BaseModel):
    label: str
    value: Decimal


class DashboardSummary(BaseModel):
    net_worth: Decimal
    accounts_balance: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_result: Decimal
    open_bills_total: Decimal
    estimated_available: Decimal | None
    warnings: list[str]


class MonthlyCashflowPoint(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal
    result: Decimal


class CategoryBreakdownItem(BaseModel):
    category: str
    amount: Decimal
    percentage: float


class RecurringExpenseItem(BaseModel):
    description: str
    category: str | None
    amount: Decimal
    occurrences: int


class CreditCardSummaryItem(BaseModel):
    id: str
    name: str
    provider: str
    limit_total: Decimal | None
    limit_available: Decimal | None
    open_bill_amount: Decimal
    due_day: int | None
    closing_day: int | None


class LargestExpenseItem(BaseModel):
    date: str
    description: str
    amount: Decimal
    category: str | None
    provider: str


class FinancialContext(BaseModel):
    analyzed_period: str
    generated_at: str
    summary: DashboardSummary
    bank_net_worth: Decimal
    accounts_balance: Decimal
    open_bills_total: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_result: Decimal
    estimated_available_until_month_end: Decimal | None
    category_breakdown: list[CategoryBreakdownItem]
    largest_expenses: list[LargestExpenseItem]
    recurring_expenses: list[RecurringExpenseItem]
    credit_cards: list[CreditCardSummaryItem]
    alerts: list[str]
    insufficient_data: list[str]
    useful_questions: list[str]
    safety_instructions: list[str]
