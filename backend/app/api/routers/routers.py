from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.email.router import router as email_router
from app.users.router import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(email_router)
api_router.include_router(user_router)