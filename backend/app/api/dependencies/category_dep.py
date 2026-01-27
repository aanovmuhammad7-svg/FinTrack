from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.finance.categories.service import CategoryService
from app.finance.categories.repository import CategoryRepository

def get_category_service(session: AsyncSession = Depends(get_async_session)):
    repo = CategoryRepository(session)
    return CategoryService(repo)