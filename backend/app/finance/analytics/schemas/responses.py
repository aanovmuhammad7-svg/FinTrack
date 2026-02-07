# app/finance/analytics/schemas.py
from pydantic import BaseModel
from decimal import Decimal


class AnalyticsSummaryResponse(BaseModel):
    income: Decimal
    expense: Decimal
    balance: Decimal


class AnalyticsByCategoryResponse(BaseModel):
    category_id: int
    category_name: str
    total: Decimal
