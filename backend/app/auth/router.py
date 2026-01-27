from fastapi import APIRouter, BackgroundTasks, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from loguru import logger

from app.db.database import get_async_session
from app.api.dependencies.redis_dep import get_redis
from app.auth.utils.cookie_handler import cookie_handler
from app.auth.schemas.requests import UserCreateRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.schemas.responses import MessageResponse, TokenResponse
from app.auth.repository import UserRepository, RefreshTokenRepository
from app.api.dependencies.limiter import limiter
from app.auth.service import RegistrationService, LoginService, RefreshService, LogoutService, PasswordResetService
from app.api.errors.exceptions import UserAlreadyExistsException, PasswordValidationErrorException, RefreshTokenNotFoundException


router = APIRouter(prefix="/auth", tags=["Авторизация пользователей"])


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def register_user(
    request: Request,
    data: UserCreateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(session=session)
    auth_service = RegistrationService(user_repo=user_repo)

    try:
        user = await auth_service.register_user(data, background_tasks)
    except UserAlreadyExistsException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e)}
        )
    except PasswordValidationErrorException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e)}
        )

    message = f"Пользователь {user.email} успешно создан"
    logger.info(f"Пользователь {user.email} успешно создан")

    if user.email_confirmed is False:
        message += "На вашу почту отправлено письмо для подтверждения регистрации."
        logger.info("На почту пользователя отправлено письмо для подтверждения регистрации")

    return MessageResponse(message=message)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
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

@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenNotFoundException

    user_repo = UserRepository(session=session)
    refresh_repo = RefreshTokenRepository(redis=redis)
    refresh_service = RefreshService(user_repo, refresh_repo)

    access_token = await refresh_service.refresh(refresh_token)

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

@router.post("/logout")
async def logout(
    request: Request,
    redis: Redis = Depends(get_redis),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return JSONResponse({"message": "Нет refresh токена"}, status_code=400)

    refresh_repo = RefreshTokenRepository(redis=redis)
    logout_service = LogoutService(refresh_repo=refresh_repo)

    await logout_service.logout(refresh_token)

    response = JSONResponse({"message": "Вы вышли из системы"})
    cookie_handler.clear_auth_tokens(response)

    return response

@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("2/minute")
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
        message="Если аккаунт существует, письмо отправлено"
    )


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
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

    return MessageResponse(message="Пароль успешно изменён")