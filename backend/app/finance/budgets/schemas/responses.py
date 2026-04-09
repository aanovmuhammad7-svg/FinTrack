from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    limit_amount: Decimal
    period_start: date
    period_end: date
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetProgressResponse(BaseModel):
    budget_id: int
    category_id: int
    category_name: str
    limit_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    utilization_percent: float
    period_start: date
    period_end: date
    is_active: bool
