from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, func, select

from app.db.models.models import Budget, Transaction
from app.db.repository import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    model = Budget

    async def list_by_user(self, user_id: int) -> Sequence[Budget]:
        result = await self.session.execute(
            select(Budget)
            .where(Budget.user_id == user_id)
            .order_by(Budget.period_start.desc(), Budget.id.desc())
        )
        return result.scalars().all()

    async def get_by_id_for_user(self, budget_id: int, user_id: int) -> Optional[Budget]:
        result = await self.session.execute(
            select(Budget)
            .where(Budget.id == budget_id)
            .where(Budget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def exists_for_period(
        self,
        *,
        user_id: int,
        category_id: int,
        period_start: date,
        period_end: date,
        exclude_budget_id: int | None = None,
    ) -> bool:
        stmt = (
            select(func.count(Budget.id))
            .where(Budget.user_id == user_id)
            .where(Budget.category_id == category_id)
            .where(Budget.period_start == period_start)
            .where(Budget.period_end == period_end)
        )
        if exclude_budget_id is not None:
            stmt = stmt.where(Budget.id != exclude_budget_id)

        count = await self.session.scalar(stmt)
        return bool(count and count > 0)

    async def calculate_spent(
        self,
        *,
        user_id: int,
        category_id: int,
        period_start: date,
        period_end: date,
    ) -> Decimal:
        start_dt = datetime.combine(period_start, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(period_end, time.max, tzinfo=timezone.utc)

        result = await self.session.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(Transaction.user_id == user_id)
            .where(Transaction.category_id == category_id)
            .where(Transaction.occurred_at >= start_dt)
            .where(Transaction.occurred_at <= end_dt)
        )
        return Decimal(result or 0)

    async def spent_by_budget(self, user_id: int) -> dict[int, Decimal]:
        tx_date = func.date(Transaction.occurred_at)
        rows = await self.session.execute(
            select(
                Budget.id.label("budget_id"),
                func.coalesce(func.sum(Transaction.amount), 0).label("spent_amount"),
            )
            .select_from(Budget)
            .outerjoin(
                Transaction,
                and_(
                    Transaction.user_id == Budget.user_id,
                    Transaction.category_id == Budget.category_id,
                    tx_date >= Budget.period_start,
                    tx_date <= Budget.period_end,
                ),
            )
            .where(Budget.user_id == user_id)
            .group_by(Budget.id)
        )
        return {row.budget_id: Decimal(row.spent_amount) for row in rows}
