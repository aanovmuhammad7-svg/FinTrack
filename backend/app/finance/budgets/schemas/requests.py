from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreateRequest(BaseModel):
    category_id: int
    limit_amount: Decimal = Field(..., gt=0)
    period_start: date
    period_end: date


class BudgetUpdateRequest(BaseModel):
    limit_amount: Decimal | None = Field(default=None, gt=0)
    period_start: date | None = None
    period_end: date | None = None
    is_active: bool | None = None
