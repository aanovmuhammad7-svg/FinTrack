from decimal import Decimal
from loguru import logger

from app.api.errors.exceptions import (
    BudgetAlreadyExists,
    BudgetCategoryTypeError,
    BudgetNotFound,
    InvalidBudgetPeriod,
)
from app.finance.budgets.repository import BudgetRepository
from app.finance.budgets.schemas.requests import BudgetCreateRequest, BudgetUpdateRequest
from app.finance.budgets.schemas.responses import BudgetProgressResponse
from app.finance.categories.repository import CategoryRepository


class BudgetService:
    def __init__(self, budget_repo: BudgetRepository, category_repo: CategoryRepository):
        self.budget_repo = budget_repo
        self.category_repo = category_repo

    async def create(self, user_id: int, data: BudgetCreateRequest):
        if data.period_start > data.period_end:
            raise InvalidBudgetPeriod()

        category = await self.category_repo.find_one_or_none(id=data.category_id, user_id=user_id)
        if not category:
            raise BudgetCategoryTypeError(data.category_id, "not_found")
        if category.type != "expense":
            raise BudgetCategoryTypeError(data.category_id, category.type)

        if await self.budget_repo.exists_for_period(
            user_id=user_id,
            category_id=data.category_id,
            period_start=data.period_start,
            period_end=data.period_end,
        ):
            raise BudgetAlreadyExists(data.category_id, data.period_start, data.period_end)

        budget = await self.budget_repo.add(
            {
                "user_id": user_id,
                "category_id": data.category_id,
                "limit_amount": data.limit_amount,
                "period_start": data.period_start,
                "period_end": data.period_end,
            }
        )
        logger.info(f"Budget created user_id={user_id} budget_id={budget.id}")
        return budget

    async def list(self, user_id: int):
        budgets = await self.budget_repo.list_by_user(user_id)
        logger.info(f"Budget list fetched user_id={user_id} count={len(budgets)}")
        return budgets

    async def get_by_id(self, user_id: int, budget_id: int):
        budget = await self.budget_repo.get_by_id_for_user(budget_id, user_id)
        if not budget:
            raise BudgetNotFound(budget_id)
        return budget

    async def update(self, user_id: int, budget_id: int, data: BudgetUpdateRequest):
        budget = await self.get_by_id(user_id, budget_id)

        new_start = data.period_start if data.period_start is not None else budget.period_start
        new_end = data.period_end if data.period_end is not None else budget.period_end
        if new_start > new_end:
            raise InvalidBudgetPeriod()

        if await self.budget_repo.exists_for_period(
            user_id=user_id,
            category_id=budget.category_id,
            period_start=new_start,
            period_end=new_end,
            exclude_budget_id=budget.id,
        ):
            raise BudgetAlreadyExists(budget.category_id, new_start, new_end)

        update_data: dict[str, object] = {}
        if data.limit_amount is not None:
            update_data["limit_amount"] = data.limit_amount
        if data.period_start is not None:
            update_data["period_start"] = data.period_start
        if data.period_end is not None:
            update_data["period_end"] = data.period_end
        if data.is_active is not None:
            update_data["is_active"] = data.is_active

        updated = await self.budget_repo.update(budget.id, update_data)
        if not updated:
            raise BudgetNotFound(budget_id)
        logger.info(f"Budget updated user_id={user_id} budget_id={budget_id} fields={list(update_data.keys())}")
        return updated

    async def delete(self, user_id: int, budget_id: int) -> None:
        budget = await self.get_by_id(user_id, budget_id)
        await self.budget_repo.delete(budget.id)
        logger.info(f"Budget deleted user_id={user_id} budget_id={budget_id}")

    async def progress(self, user_id: int):
        budgets = await self.budget_repo.list_by_user(user_id)
        spent_map = await self.budget_repo.spent_by_budget(user_id)
        items: list[BudgetProgressResponse] = []

        for budget in budgets:
            spent = spent_map.get(budget.id, Decimal(0))
            remaining = Decimal(budget.limit_amount) - Decimal(spent)
            utilization = 0.0
            if budget.limit_amount > 0:
                utilization = float((Decimal(spent) / Decimal(budget.limit_amount)) * Decimal(100))

            items.append(
                BudgetProgressResponse(
                    budget_id=budget.id,
                    category_id=budget.category_id,
                    category_name=budget.category.name,
                    limit_amount=Decimal(budget.limit_amount),
                    spent_amount=Decimal(spent),
                    remaining_amount=remaining,
                    utilization_percent=round(utilization, 2),
                    period_start=budget.period_start,
                    period_end=budget.period_end,
                    is_active=budget.is_active,
                )
            )

        return items
