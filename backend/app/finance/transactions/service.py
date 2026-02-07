# app/finance/transactions/service.py
from typing import Sequence, Dict, Any, cast

from app.finance.transactions.repository import TransactionRepository
from app.finance.categories.repository import CategoryRepository
from app.finance.transactions.schemas.requests import (
    TransactionCreate,
    TransactionUpdate,
)
from app.finance.transactions.schemas.filters import TransactionFilter
from app.db.models.models import Transaction
from app.api.errors.exceptions import (
    TransactionNotFound,
    InvalidTransactionAmount,
    TransactionCategoryAccessDenied,
)

ALLOWED_TRANSACTION_TYPES = {"income", "expense"}


class TransactionService:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ):
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo

    # --- CREATE ---
    async def create(self, user_id: int, data: TransactionCreate) -> Transaction:
        # 1️⃣ Валидация суммы
        if data.amount <= 0:
            raise InvalidTransactionAmount(data.amount)

        # 3️⃣ Проверка доступа к категории
        category = await self.category_repo.find_one_or_none(
            id=data.category_id,
            user_id=user_id,
        )
        if not category:
            raise TransactionCategoryAccessDenied(data.category_id)

        # 4️⃣ Создание транзакции
        return await self.transaction_repo.add(
            {
                "user_id": user_id,
                "category_id": data.category_id,
                "amount": data.amount,
                "description": data.description,
                "occurred_at": data.occurred_at,
            }
        )

    # --- LIST ---
    async def list(self, user_id: int) -> Sequence[Transaction]:
        return await self.transaction_repo.list_by_user(user_id=user_id)

    # --- GET BY ID ---
    async def get_by_id(self, user_id: int, transaction_id: int) -> Transaction:
        transaction = await self.transaction_repo.get_by_id_for_user(
            transaction_id=transaction_id,
            user_id=user_id,
        )
        if not transaction:
            raise TransactionNotFound(transaction_id)

        return transaction

    # --- UPDATE ---
    async def update(
        self,
        user_id: int,
        transaction_id: int,
        data: TransactionUpdate,
    ) -> Transaction:
        transaction = await self.get_by_id(user_id, transaction_id)

        update_data: Dict[str, Any] = {}

        if data.amount is not None:
            if data.amount <= 0:
                raise InvalidTransactionAmount(data.amount)
            update_data["amount"] = data.amount

        if data.category_id is not None:
            category = await self.category_repo.find_one_or_none(
                id=data.category_id,
                user_id=user_id,
            )
            if not category:
                raise TransactionCategoryAccessDenied(data.category_id)
            update_data["category_id"] = data.category_id

        if data.description is not None:
            update_data["description"] = data.description

        if data.occurred_at is not None:
            update_data["occurred_at"] = data.occurred_at

        updated = await self.transaction_repo.update(
            model_id=transaction.id,
            data=update_data,
        )

        return cast(Transaction, updated)

    # --- DELETE ---
    async def delete(self, user_id: int, transaction_id: int) -> None:
        await self.get_by_id(user_id, transaction_id)
        await self.transaction_repo.delete_for_user(
            transaction_id=transaction_id,
            user_id=user_id,
        )

    async def list_filtered(
        self,
        user_id: int,
        filters: TransactionFilter,
        limit: int,
        offset: int,
    ):
        return await self.transaction_repo.list_by_user_filtered(
            user_id=user_id,
            **filters.model_dump(exclude_none=True),  # ✅ распаковка
            limit=limit,
            offset=offset,
        )
