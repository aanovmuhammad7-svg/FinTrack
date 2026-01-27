from sqlalchemy import select, exists
from typing import Any, Sequence
from app.db.models.models import Category
from app.db.repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    async def exists_by_name_and_type(
        self, *, user_id: int, name: str, type: str
    ) -> bool:
        stmt = select(
            exists().where(
                Category.user_id == user_id,
                Category.name == name,
                Category.type == type
            )
        )
        result = await self.session.scalar(stmt)
        return bool(result)

    async def create(
        self,
        *,
        user_id: int,
        name: str,
        type: str,
    ) -> Category:
        data: dict[str, Any] = {
        "user_id": user_id,
        "name": name,
        "type": type
        }
        return await super().add(data)

    async def get_all_by_user(
        self, *, user_id: int
    ) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category).where(Category.user_id == user_id)
        )
        return result.scalars().all()
