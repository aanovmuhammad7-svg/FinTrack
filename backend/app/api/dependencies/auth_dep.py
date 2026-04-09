from datetime import datetime, timezone
from fastapi import Depends, Request

from app.db.models.models import User
from app.auth.repository import UserRepository
from app.auth.utils.jwt_handler import jwt_handler
from app.api.dependencies.repo_dep import get_user_repository
from app.api.errors.exceptions import (
    AccessTokenNotFoundException,
    RefreshTokenNotFoundException,
    InvalidTokenException,
    UserNotFoundException,
    UserInactiveException,
    CSRFMissingOrInvalidException,
)


async def get_access_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise AccessTokenNotFoundException
    return token


async def get_refresh_token(request: Request) -> str:
    token = request.cookies.get("refresh_token")
    if not token:
        raise RefreshTokenNotFoundException
    return token


async def verify_csrf(request: Request) -> None:
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")

    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise CSRFMissingOrInvalidException


async def get_current_user(
    token: str = Depends(get_access_token),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    payload = jwt_handler.decode(
        token,
        required_claims=("sub", "user_id", "jti", "iat", "exp"),
    )
    if not payload:
        raise InvalidTokenException

    email = payload.get("sub")
    if not email:
        raise InvalidTokenException

    try:
        user_id = int(payload.get("user_id"))
    except (TypeError, ValueError):
        raise InvalidTokenException

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundException(email)
    if not user.is_active:
        raise UserInactiveException

    # защита от старых токенов после смены пароля
    token_pwd_reset_at = int(payload.get("pwd_reset_at", 0))
    token_pwd_reset_at_dt = datetime.fromtimestamp(
        token_pwd_reset_at,
        tz=timezone.utc,
    ).replace(microsecond=0)

    if user.last_password_reset:
        user_pwd_reset_at = user.last_password_reset.astimezone(
            timezone.utc
        ).replace(microsecond=0)
        if token_pwd_reset_at_dt < user_pwd_reset_at:
            raise InvalidTokenException

    return user
