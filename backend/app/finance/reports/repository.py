from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import NamedTuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Budget, Category, Transaction


class ReportCategoryRow(NamedTuple):
    category_id: int
    category_name: str
    category_type: str
    total: Decimal


class ReportDailyRow(NamedTuple):
    day: date
    category_type: str
    total: Decimal


class ReportBudgetRow(NamedTuple):
    budget_id: int
    category_id: int
    category_name: str
    limit_amount: Decimal
    period_start: date
    period_end: date
    spent_amount: Decimal


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _bounds(date_from: date, date_to: date) -> tuple[datetime, datetime]:
        start_dt = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
        return start_dt, end_dt

    async def summary(self, user_id: int, date_from: date, date_to: date) -> tuple[Decimal, Decimal]:
        start_dt, end_dt = self._bounds(date_from, date_to)

        rows = await self.session.execute(
            select(Transaction.amount, Category.type)
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
            .where(Transaction.occurred_at >= start_dt)
            .where(Transaction.occurred_at <= end_dt)
        )

        income = Decimal(0)
        expense = Decimal(0)
        for amount, category_type in rows:
            if category_type == "income":
                income += Decimal(amount)
            else:
                expense += Decimal(amount)

        return income, expense

    async def by_category(
        self,
        user_id: int,
        date_from: date,
        date_to: date,
    ) -> list[ReportCategoryRow]:
        start_dt, end_dt = self._bounds(date_from, date_to)
        rows = await self.session.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                Category.type.label("category_type"),
                func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
            .where(Transaction.occurred_at >= start_dt)
            .where(Transaction.occurred_at <= end_dt)
            .group_by(Category.id, Category.name, Category.type)
            .order_by(func.coalesce(func.sum(Transaction.amount), 0).desc())
        )
        return [
            ReportCategoryRow(
                category_id=int(row.category_id),
                category_name=str(row.category_name),
                category_type=str(row.category_type),
                total=Decimal(row.total),
            )
            for row in rows
        ]

    async def daily(
        self,
        user_id: int,
        date_from: date,
        date_to: date,
    ) -> list[ReportDailyRow]:
        start_dt, end_dt = self._bounds(date_from, date_to)
        rows = await self.session.execute(
            select(
                func.date(Transaction.occurred_at).label("day"),
                Category.type.label("category_type"),
                func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
            .where(Transaction.occurred_at >= start_dt)
            .where(Transaction.occurred_at <= end_dt)
            .group_by(func.date(Transaction.occurred_at), Category.type)
            .order_by(func.date(Transaction.occurred_at).asc())
        )
        return [
            ReportDailyRow(
                day=row.day,
                category_type=str(row.category_type),
                total=Decimal(row.total),
            )
            for row in rows
        ]

    async def budgets(
        self,
        user_id: int,
        date_from: date,
        date_to: date,
    ) -> list[ReportBudgetRow]:
        tx_date = func.date(Transaction.occurred_at)
        rows = await self.session.execute(
            select(
                Budget.id.label("budget_id"),
                Budget.category_id,
                Category.name.label("category_name"),
                Budget.limit_amount,
                Budget.period_start,
                Budget.period_end,
                func.coalesce(func.sum(Transaction.amount), 0).label("spent_amount"),
            )
            .select_from(Budget)
            .join(Category, Budget.category_id == Category.id)
            .outerjoin(
                Transaction,
                and_(
                    Transaction.user_id == Budget.user_id,
                    Transaction.category_id == Budget.category_id,
                    tx_date >= Budget.period_start,
                    tx_date <= Budget.period_end,
                    tx_date >= date_from,
                    tx_date <= date_to,
                ),
            )
            .where(Budget.user_id == user_id)
            .where(Budget.is_active.is_(True))
            .where(Budget.period_start <= date_to)
            .where(Budget.period_end >= date_from)
            .group_by(
                Budget.id,
                Budget.category_id,
                Category.name,
                Budget.limit_amount,
                Budget.period_start,
                Budget.period_end,
            )
            .order_by(Budget.period_start.desc())
        )
        return [
            ReportBudgetRow(
                budget_id=int(row.budget_id),
                category_id=int(row.category_id),
                category_name=str(row.category_name),
                limit_amount=Decimal(row.limit_amount),
                period_start=row.period_start,
                period_end=row.period_end,
                spent_amount=Decimal(row.spent_amount),
            )
            for row in rows
        ]
