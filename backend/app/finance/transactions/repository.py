# app/finance/transactions/repository.py
from decimal import Decimal
from typing import Optional, Sequence
from datetime import datetime

from sqlalchemy import select, func, delete

from app.db.models.models import Transaction
from app.db.repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    model = Transaction

    # Получить все транзакции конкретного пользователя
    async def list_by_user(self, user_id: int) -> Sequence[Transaction]:
        return await self.get_all(user_id=user_id)

    # Получить транзакцию по ID и user_id (чтобы нельзя было получить чужую)
    async def get_by_id_for_user(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        result = await self.session.execute(
            select(self.model)
            .where(self.model.id == transaction_id)
            .where(self.model.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # Получить сумму транзакций по категории
    async def sum_amounts_by_category(self, user_id: int, category_id: int) -> Decimal:
        stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or Decimal(0)

    # Удаление транзакции по ID и user_id (чтобы нельзя было удалить чужую)
    async def delete_for_user(self, transaction_id: int, user_id: int) -> None:
        stmt = delete(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    )
        await self.session.execute(stmt)
        await self.session.commit()

    async def list_by_user_filtered( self, user_id: int, *,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        category_id: Optional[int] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        stmt = select(Transaction).where(Transaction.user_id == user_id)

        if date_from:
            stmt = stmt.where(Transaction.occurred_at >= date_from)

        if date_to:
            stmt = stmt.where(Transaction.occurred_at <= date_to)

        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)

        if min_amount:
            stmt = stmt.where(Transaction.amount >= min_amount)

        if max_amount:
            stmt = stmt.where(Transaction.amount <= max_amount)

        if search:
            stmt = stmt.where(Transaction.description.ilike(f"%{search}%"))

        stmt = stmt.order_by(Transaction.occurred_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()
