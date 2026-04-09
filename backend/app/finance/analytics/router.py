from typing import List

from fastapi import APIRouter, Depends, Request

from app.api.dependencies.analytics_dep import get_analytics_service
from app.api.dependencies.auth_dep import get_current_user
from app.api.dependencies.limiter import limiter
from app.db.models.models import User
from app.finance.analytics.schemas.responses import AnalyticsByCategoryResponse, AnalyticsSummaryResponse
from app.finance.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse, summary="Income and expense summary")
@limiter.limit("30/minute")
async def get_summary(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.summary(user_id=current_user.id)


@router.get("/by-category", response_model=List[AnalyticsByCategoryResponse], summary="Totals by category")
@limiter.limit("30/minute")
async def get_by_category(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.by_category(user_id=current_user.id)
