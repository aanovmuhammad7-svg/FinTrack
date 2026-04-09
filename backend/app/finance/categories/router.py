from typing import List

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies.auth_dep import get_current_user, verify_csrf
from app.api.dependencies.category_dep import get_category_service
from app.api.dependencies.limiter import limiter
from app.db.models.models import User
from app.finance.categories.schemas.requests import CategoryCreateRequest, CategoryUpdateRequest
from app.finance.categories.schemas.responses import CategoryResponse
from app.finance.categories.service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Create category")
@limiter.limit("30/minute")
async def create_category(
    request: Request,
    data: CategoryCreateRequest,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return await service.create(user_id=current_user.id, data=data)


@router.get("/", response_model=List[CategoryResponse], summary="List categories")
@limiter.limit("60/minute")
async def list_categories(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return await service.list(user_id=current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse, summary="Get category by id")
@limiter.limit("60/minute")
async def get_category(
    request: Request,
    category_id: int,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_by_id(user_id=current_user.id, category_id=category_id)


@router.patch("/{category_id}", response_model=CategoryResponse, summary="Update category")
@limiter.limit("30/minute")
async def update_category(
    request: Request,
    category_id: int,
    data: CategoryUpdateRequest,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return await service.update(user_id=current_user.id, category_id=category_id, data=data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete category")
@limiter.limit("30/minute")
async def delete_category(
    request: Request,
    category_id: int,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    await service.delete(user_id=current_user.id, category_id=category_id)
