from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.finance.transactions.repository import TransactionRepository
from app.finance.categories.repository import CategoryRepository
from app.finance.transactions.service import TransactionService


def get_transaction_service(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionService:
    transaction_repo = TransactionRepository(session)
    category_repo = CategoryRepository(session)

    return TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
    )
