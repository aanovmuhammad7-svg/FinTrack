from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.email.router import router as email_router
from app.users.router import router as user_router
from app.finance.categories.router import router as categories_router
from app.finance.transactions.router import router as transactions
from app.finance.analytics.router import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(email_router)
api_router.include_router(user_router)
api_router.include_router(categories_router)
api_router.include_router(transactions)
api_router.include_router(analytics_router)