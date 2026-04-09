from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dep import verify_csrf
from app.api.dependencies.limiter import limiter
from app.api.dependencies.redis_dep import get_redis
from app.api.errors.exceptions import InvalidTokenException, RefreshTokenNotFoundException
from app.auth.repository import RefreshTokenRepository, UserRepository
from app.auth.schemas.requests import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    UserCreateRequest,
)
from app.auth.schemas.responses import MessageResponse, TokenResponse
from app.auth.service import (
    LoginService,
    LogoutService,
    PasswordResetService,
    RefreshService,
    RegistrationService,
)
from app.auth.utils.cookie_handler import cookie_handler
from app.db.database import get_async_session


router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
)
@limiter.limit("10/hour")
async def register_user(
    request: Request,
    data: UserCreateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(session=session)
    auth_service = RegistrationService(user_repo=user_repo)

    user = await auth_service.register_user(data, background_tasks)

    message = f"User {user.email} was created successfully"
    logger.info(f"User {user.email} was created successfully")

    if user.email_confirmed is False:
        message += " Confirmation email was sent."
        logger.info("Confirmation email was queued for delivery")

    return MessageResponse(message=message)


@router.post("/login", response_model=TokenResponse, summary="Login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
):
    user_repo = UserRepository(session=session)
    refresh_repo = RefreshTokenRepository(redis=redis)
    auth_service = LoginService(user_repo, refresh_repo)

    access_token, refresh_token = await auth_service.login_user(
        email=data.email,
        password=data.password,
    )

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
        }
    )

    cookie_handler.set_auth_tokens(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    return response


@router.post("/refresh", summary="Refresh tokens")
@limiter.limit("30/minute")
async def refresh(
    request: Request,
    _: None = Depends(verify_csrf),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenNotFoundException

    user_repo = UserRepository(session=session)
    refresh_repo = RefreshTokenRepository(redis=redis)
    refresh_service = RefreshService(user_repo, refresh_repo)

    access_token, new_refresh_token = await refresh_service.refresh(refresh_token)

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
        }
    )

    csrf_token = request.cookies.get("csrf_token")
    cookie_handler.set_auth_tokens(
        response=response,
        access_token=access_token,
        refresh_token=new_refresh_token,
        csrf_token=csrf_token,
    )

    return response


@router.post("/logout", summary="Logout")
@limiter.limit("30/minute")
async def logout(
    request: Request,
    _: None = Depends(verify_csrf),
    redis: Redis = Depends(get_redis),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        refresh_repo = RefreshTokenRepository(redis=redis)
        logout_service = LogoutService(refresh_repo=refresh_repo)
        try:
            await logout_service.logout(refresh_token)
        except InvalidTokenException:
            logger.warning("Logout requested with invalid refresh token")

    response = JSONResponse({"message": "You have been logged out"})
    cookie_handler.clear_auth_tokens(response)

    return response


@router.post("/forgot-password", response_model=MessageResponse, summary="Request password reset")
@limiter.limit("3/15minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
):
    service = PasswordResetService(
        user_repo=UserRepository(session),
        refresh_repo=RefreshTokenRepository(redis),
    )

    await service.forgot_password(data.email)

    return MessageResponse(
        message="If the account exists, the reset email was sent"
    )


@router.post("/reset-password", response_model=MessageResponse, summary="Reset password")
@limiter.limit("5/15minute")
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
):
    service = PasswordResetService(
        user_repo=UserRepository(session),
        refresh_repo=RefreshTokenRepository(redis),
    )

    await service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )

    return MessageResponse(message="Password was changed successfully")
