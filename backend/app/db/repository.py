from typing import Generic, TypeVar, Type, Any, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.models.base import IDMixin


T = TypeVar("T", bound=IDMixin)


class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, model_id: int) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == model_id)
        )
        return result.scalar_one_or_none()
    
    async def find_one_or_none(self, **filters: Any) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).filter_by(**filters)
        )
        return result.scalar_one_or_none()

    async def get_all(self, **filters: Any) -> Sequence[T]:
        result = await self.session.execute(
            select(self.model).filter_by(**filters)
        )
        return result.scalars().all()

    async def add(self, data: dict[str, Any]) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, model_id: int, data: dict[str, Any]) -> Optional[T]:
        stmt = (
            update(self.model)
            .where(self.model.id == model_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, model_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == model_id)
        await self.session.execute(stmt)
        await self.session.commit()
