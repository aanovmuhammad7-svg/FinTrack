from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.modules.auth.schema import RegisterRequest, LoginRequest, TokenResponse
from app.modules.auth.service import register_user, authenticate_user
from app.modules.auth.dependencies import get_current_user
from app.modules.users.schema import UserRead
from app.modules.users.model import User

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        token = await register_user(session, data)
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        token = await authenticate_user(session, data)
        return {"access_token": token}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
