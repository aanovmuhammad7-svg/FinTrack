from datetime import date

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.auth_dep import get_current_user
from app.api.dependencies.limiter import limiter
from app.api.dependencies.report_dep import get_report_service
from app.db.models.models import User
from app.finance.reports.schemas.responses import (
    ReportBudgetItem,
    ReportCategoryItem,
    ReportDailyItem,
    ReportOverviewResponse,
    ReportSummaryResponse,
)
from app.finance.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=ReportSummaryResponse, summary="Report summary")
@limiter.limit("30/minute")
async def summary_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return await service.summary(user_id=current_user.id, date_from=date_from, date_to=date_to)


@router.get("/by-category", response_model=list[ReportCategoryItem], summary="Report by category")
@limiter.limit("30/minute")
async def by_category_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return await service.by_category(user_id=current_user.id, date_from=date_from, date_to=date_to)


@router.get("/daily", response_model=list[ReportDailyItem], summary="Daily report")
@limiter.limit("30/minute")
async def daily_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return await service.daily(user_id=current_user.id, date_from=date_from, date_to=date_to)


@router.get("/budgets", response_model=list[ReportBudgetItem], summary="Budget execution report")
@limiter.limit("30/minute")
async def budget_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return await service.budgets(user_id=current_user.id, date_from=date_from, date_to=date_to)


@router.get("/overview", response_model=ReportOverviewResponse, summary="Combined report overview")
@limiter.limit("30/minute")
async def overview_report(
    request: Request,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    return await service.overview(user_id=current_user.id, date_from=date_from, date_to=date_to)
