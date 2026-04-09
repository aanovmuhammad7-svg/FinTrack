from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.finance.reports.repository import ReportRepository
from app.finance.reports.service import ReportService


def get_report_service(
    session: AsyncSession = Depends(get_async_session),
) -> ReportService:
    repo = ReportRepository(session)
    return ReportService(repo=repo)
