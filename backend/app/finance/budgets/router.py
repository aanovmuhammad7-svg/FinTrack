from typing import List

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies.auth_dep import get_current_user, verify_csrf
from app.api.dependencies.budget_dep import get_budget_service
from app.api.dependencies.limiter import limiter
from app.db.models.models import User
from app.finance.budgets.schemas.requests import BudgetCreateRequest, BudgetUpdateRequest
from app.finance.budgets.schemas.responses import BudgetProgressResponse, BudgetResponse
from app.finance.budgets.service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED, summary="Create budget")
@limiter.limit("20/minute")
async def create_budget(
    request: Request,
    data: BudgetCreateRequest,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    return await service.create(user_id=current_user.id, data=data)


@router.get("/", response_model=List[BudgetResponse], summary="List budgets")
@limiter.limit("60/minute")
async def list_budgets(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    return await service.list(user_id=current_user.id)


@router.get("/progress", response_model=List[BudgetProgressResponse], summary="Budget progress")
@limiter.limit("60/minute")
async def budget_progress(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    return await service.progress(user_id=current_user.id)


@router.get("/{budget_id}", response_model=BudgetResponse, summary="Get budget")
@limiter.limit("60/minute")
async def get_budget(
    request: Request,
    budget_id: int,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    return await service.get_by_id(user_id=current_user.id, budget_id=budget_id)


@router.patch("/{budget_id}", response_model=BudgetResponse, summary="Update budget")
@limiter.limit("20/minute")
async def update_budget(
    request: Request,
    budget_id: int,
    data: BudgetUpdateRequest,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    return await service.update(user_id=current_user.id, budget_id=budget_id, data=data)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete budget")
@limiter.limit("20/minute")
async def delete_budget(
    request: Request,
    budget_id: int,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    await service.delete(user_id=current_user.id, budget_id=budget_id)
