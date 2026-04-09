from datetime import date
from decimal import Decimal

from loguru import logger

from app.api.errors.exceptions import InvalidReportPeriod
from app.finance.reports.repository import ReportRepository
from app.finance.reports.schemas.responses import (
    ReportBudgetItem,
    ReportCategoryItem,
    ReportDailyItem,
    ReportOverviewResponse,
    ReportSummaryResponse,
)


class ReportService:
    def __init__(self, repo: ReportRepository):
        self.repo = repo

    @staticmethod
    def _validate_period(date_from: date, date_to: date) -> None:
        if date_from > date_to:
            raise InvalidReportPeriod()

    async def summary(self, user_id: int, date_from: date, date_to: date) -> ReportSummaryResponse:
        self._validate_period(date_from, date_to)
        income, expense = await self.repo.summary(user_id, date_from, date_to)
        logger.info(
            f"Report summary generated user_id={user_id} date_from={date_from} date_to={date_to}"
        )
        return ReportSummaryResponse(
            date_from=date_from,
            date_to=date_to,
            income=income,
            expense=expense,
            balance=income - expense,
        )

    async def by_category(self, user_id: int, date_from: date, date_to: date) -> list[ReportCategoryItem]:
        self._validate_period(date_from, date_to)
        rows = await self.repo.by_category(user_id, date_from, date_to)
        return [
            ReportCategoryItem(
                category_id=row.category_id,
                category_name=row.category_name,
                category_type=row.category_type,
                total=Decimal(row.total),
            )
            for row in rows
        ]

    async def daily(self, user_id: int, date_from: date, date_to: date) -> list[ReportDailyItem]:
        self._validate_period(date_from, date_to)
        rows = await self.repo.daily(user_id, date_from, date_to)

        by_day: dict[date, dict[str, Decimal]] = {}
        for row in rows:
            day_bucket = by_day.setdefault(row.day, {"income": Decimal(0), "expense": Decimal(0)})
            day_bucket[row.category_type] += Decimal(row.total)

        return [
            ReportDailyItem(
                day=day,
                income=values["income"],
                expense=values["expense"],
                balance=values["income"] - values["expense"],
            )
            for day, values in sorted(by_day.items(), key=lambda x: x[0])
        ]

    async def budgets(self, user_id: int, date_from: date, date_to: date) -> list[ReportBudgetItem]:
        self._validate_period(date_from, date_to)
        rows = await self.repo.budgets(user_id, date_from, date_to)

        result: list[ReportBudgetItem] = []
        for row in rows:
            spent_amount = Decimal(row.spent_amount)

            limit_amount = Decimal(row.limit_amount)
            remaining = limit_amount - spent_amount
            utilization = float((spent_amount / limit_amount) * Decimal(100)) if limit_amount > 0 else 0.0

            result.append(
                ReportBudgetItem(
                    budget_id=row.budget_id,
                    category_id=row.category_id,
                    category_name=row.category_name,
                    limit_amount=limit_amount,
                    spent_amount=spent_amount,
                    remaining_amount=remaining,
                    utilization_percent=round(utilization, 2),
                    period_start=row.period_start,
                    period_end=row.period_end,
                )
            )

        return result

    async def overview(self, user_id: int, date_from: date, date_to: date) -> ReportOverviewResponse:
        summary = await self.summary(user_id, date_from, date_to)
        by_category = await self.by_category(user_id, date_from, date_to)
        daily = await self.daily(user_id, date_from, date_to)
        budgets = await self.budgets(user_id, date_from, date_to)

        return ReportOverviewResponse(
            summary=summary,
            by_category=by_category,
            daily=daily,
            budgets=budgets,
        )
