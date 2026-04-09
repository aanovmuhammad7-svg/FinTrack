from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.finance.budgets.repository import BudgetRepository
from app.finance.budgets.service import BudgetService
from app.finance.categories.repository import CategoryRepository


def get_budget_service(
    session: AsyncSession = Depends(get_async_session),
) -> BudgetService:
    budget_repo = BudgetRepository(session)
    category_repo = CategoryRepository(session)
    return BudgetService(budget_repo=budget_repo, category_repo=category_repo)
