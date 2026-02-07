# app/finance/analytics/router.py
from fastapi import APIRouter, Depends
from typing import List

from app.api.dependencies.auth_dep import get_current_user
from app.db.models.models import User
from app.finance.analytics.service import AnalyticsService
from app.finance.analytics.schemas.responses import (
    AnalyticsSummaryResponse,
    AnalyticsByCategoryResponse,
)
from app.api.dependencies.analytics_dep import get_analytics_service

router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_summary(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.summary(user_id=current_user.id)


@router.get("/by-category", response_model=List[AnalyticsByCategoryResponse])
async def get_by_category(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.by_category(user_id=current_user.id)
