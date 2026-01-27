from typing import Sequence, Dict, Any, cast
from app.finance.categories.repository import CategoryRepository
from app.api.errors.exceptions import (
    CategoryAlreadyExists,
    CategoryNotFound,
    InvalidCategoryType
)
from app.finance.categories.schemas.requests import CategoryCreateRequest, CategoryUpdateRequest
from app.db.models.models import Category


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.repo = category_repo

    async def create(self, user_id: int, data: CategoryCreateRequest) -> Category:
        # Проверка типа категории
        if data.type not in ("income", "expense"):
            raise InvalidCategoryType(data.type)

        # Проверка существующей категории
        exists = await self.repo.exists_by_name_and_type(
            user_id=user_id, name=data.name, type=data.type
        )
        if exists:
            raise CategoryAlreadyExists(name=data.name, type=data.type)

        # Создаём категорию
        return await self.repo.create(user_id=user_id, name=data.name, type=data.type)

    async def list(self, user_id: int) -> Sequence[Category]:
        return await self.repo.get_all_by_user(user_id=user_id)

    async def get_by_id(self, user_id: int, category_id: int) -> Category:
        category = await self.repo.get_by_id(category_id)
        if not category or category.user_id != user_id:
            raise CategoryNotFound(category_id)
        return category

    async def update(self, user_id: int, category_id: int, data: CategoryUpdateRequest) -> Category:
        category = await self.get_by_id(user_id, category_id)

        update_data: Dict[str, Any] = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.type is not None:
            update_data["type"] = data.type

        # Проверка на дубли при изменении имени или типа
        if ("name" in update_data or "type" in update_data):
            new_name = update_data.get("name", category.name)
            new_type = update_data.get("type", category.type)
            exists = await self.repo.exists_by_name_and_type(
                user_id=user_id, name=new_name, type=new_type
            )
            if exists and (new_name != category.name or new_type != category.type):
                raise CategoryAlreadyExists(name=new_name, type=new_type)

        updated_category = cast(Category, await self.repo.update(category_id, update_data))
        return updated_category

    async def delete(self, user_id: int, category_id: int) -> None:
        category = await self.get_by_id(user_id, category_id)
        await self.repo.delete(category.id)
