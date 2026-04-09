from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ReportSummaryResponse(BaseModel):
    date_from: date
    date_to: date
    income: Decimal
    expense: Decimal
    balance: Decimal


class ReportCategoryItem(BaseModel):
    category_id: int
    category_name: str
    category_type: str
    total: Decimal


class ReportDailyItem(BaseModel):
    day: date
    income: Decimal
    expense: Decimal
    balance: Decimal


class ReportBudgetItem(BaseModel):
    budget_id: int
    category_id: int
    category_name: str
    limit_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    utilization_percent: float
    period_start: date
    period_end: date


class ReportOverviewResponse(BaseModel):
    summary: ReportSummaryResponse
    by_category: list[ReportCategoryItem]
    daily: list[ReportDailyItem]
    budgets: list[ReportBudgetItem]
