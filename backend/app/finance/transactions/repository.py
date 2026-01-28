# app/finance/transactions/repository.py
from decimal import Decimal
from typing import Optional, Sequence

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
