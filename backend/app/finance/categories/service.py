from typing import Any, Dict, Sequence, cast

from loguru import logger

from app.api.errors.exceptions import CategoryAlreadyExists, CategoryNotFound, InvalidCategoryType
from app.db.models.models import Category
from app.finance.categories.repository import CategoryRepository
from app.finance.categories.schemas.requests import CategoryCreateRequest, CategoryUpdateRequest


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.repo = category_repo

    async def create(self, user_id: int, data: CategoryCreateRequest) -> Category:
        if data.type not in ("income", "expense"):
            logger.warning(f"Category create rejected: invalid type user_id={user_id} type={data.type}")
            raise InvalidCategoryType(data.type)

        exists = await self.repo.exists_by_name_and_type(
            user_id=user_id,
            name=data.name,
            type=data.type,
        )
        if exists:
            logger.warning(
                f"Category create rejected: duplicate user_id={user_id} name={data.name} type={data.type}"
            )
            raise CategoryAlreadyExists(name=data.name, type=data.type)

        category = await self.repo.create(user_id=user_id, name=data.name, type=data.type)
        logger.info(
            f"Category created user_id={user_id} category_id={category.id} name={category.name} type={category.type}"
        )
        return category

    async def list(self, user_id: int) -> Sequence[Category]:
        categories = await self.repo.get_all_by_user(user_id=user_id)
        logger.info(f"Category list fetched user_id={user_id} count={len(categories)}")
        return categories

    async def get_by_id(self, user_id: int, category_id: int) -> Category:
        category = await self.repo.get_by_id(category_id)
        if not category or category.user_id != user_id:
            logger.warning(
                f"Category get rejected: not found or denied user_id={user_id} category_id={category_id}"
            )
            raise CategoryNotFound(category_id)
        return category

    async def update(self, user_id: int, category_id: int, data: CategoryUpdateRequest) -> Category:
        category = await self.get_by_id(user_id, category_id)

        update_data: Dict[str, Any] = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.type is not None:
            update_data["type"] = data.type

        if "name" in update_data or "type" in update_data:
            new_name = update_data.get("name", category.name)
            new_type = update_data.get("type", category.type)
            exists = await self.repo.exists_by_name_and_type(
                user_id=user_id,
                name=new_name,
                type=new_type,
            )
            if exists and (new_name != category.name or new_type != category.type):
                logger.warning(
                    f"Category update rejected: duplicate user_id={user_id} category_id={category_id} name={new_name} type={new_type}"
                )
                raise CategoryAlreadyExists(name=new_name, type=new_type)

        updated_category = cast(Category, await self.repo.update(category_id, update_data))
        logger.info(
            f"Category updated user_id={user_id} category_id={category_id} fields={list(update_data.keys())}"
        )
        return updated_category

    async def delete(self, user_id: int, category_id: int) -> None:
        category = await self.get_by_id(user_id, category_id)
        await self.repo.delete(category.id)
        logger.info(f"Category deleted user_id={user_id} category_id={category_id}")
