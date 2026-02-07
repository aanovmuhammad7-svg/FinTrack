# app/finance/analytics/repository.py
from sqlalchemy import select, func
from decimal import Decimal

from app.db.models.models import Transaction, Category
from app.db.repository import BaseRepository


class AnalyticsRepository(BaseRepository[Transaction]):
    model = Transaction

    async def summary(self, user_id: int):
        rows = await self.session.execute(
            select(Transaction.amount, Category.type)
            .join(Category)
            .where(Transaction.user_id == user_id)
        )
    
        income = Decimal(0)
        expense = Decimal(0)

        for amount, category_type in rows:
            if category_type == 'income':
                income += amount
            else:
                expense += amount

        return income, expense

    async def by_category(self, user_id: int):
        rows = await self.session.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.sum(Transaction.amount).label("total")
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
            .group_by(Category.id)
        )
        return rows.all()  # возвращает список Row
