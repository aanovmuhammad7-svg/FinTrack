from fastapi import APIRouter, Depends, status
from typing import List

from app.api.dependencies.auth_dep import get_current_user
from app.db.models.models import User
from app.finance.categories.schemas.requests import CategoryCreateRequest, CategoryUpdateRequest
from app.finance.categories.schemas.responses import CategoryResponse
from app.finance.categories.service import CategoryService
from app.api.dependencies.category_dep import get_category_service

router = APIRouter(prefix="/categories", tags=["Категории для Транзакций"])


# --- CREATE ---
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    """
    Создать категорию для пользователя
    """
    return await service.create(user_id=current_user.id, data=data)


# --- LIST ---
@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    """
    Получить все категории пользователя
    """
    return await service.list(user_id=current_user.id)


# --- GET BY ID ---
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    """
    Получить конкретную категорию по ID
    """
    return await service.get_by_id(user_id=current_user.id, category_id=category_id)


# --- UPDATE ---
@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    """
    Обновить категорию
    """
    return await service.update(user_id=current_user.id, category_id=category_id, data=data)


# --- DELETE ---
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    """
    Удалить категорию
    """
    await service.delete(user_id=current_user.id, category_id=category_id)
