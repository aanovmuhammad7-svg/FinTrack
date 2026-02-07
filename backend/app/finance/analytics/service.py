# app/finance/analytics/service.py
from typing import List

from app.finance.analytics.repository import AnalyticsRepository
from app.finance.analytics.schemas.responses import (
    AnalyticsSummaryResponse,
    AnalyticsByCategoryResponse,
)


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    async def summary(self, user_id: int) -> AnalyticsSummaryResponse:
        income, expense = await self.repo.summary(user_id)

        return AnalyticsSummaryResponse(
            income=income,
            expense=expense,
            balance=income-expense,
        )

    async def by_category(self, user_id: int) -> List[AnalyticsByCategoryResponse]:
        rows = await self.repo.by_category(user_id)

        return [
            AnalyticsByCategoryResponse(
                category_id=row.category_id,
                category_name=row.category_name,
                total=row.total,
            )
            for row in rows
        ]
