# app/api/dependencies/analytics_dep.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.finance.analytics.repository import AnalyticsRepository
from app.finance.analytics.service import AnalyticsService


def get_analytics_service(
    session: AsyncSession = Depends(get_async_session),
) -> AnalyticsService:
    repo = AnalyticsRepository(session)
    return AnalyticsService(repo)
