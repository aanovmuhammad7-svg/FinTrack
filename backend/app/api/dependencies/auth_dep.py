from datetime import datetime
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


async def get_current_user(
    token: str = Depends(get_access_token),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    payload = jwt_handler.decode(token)
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

    # защита от старых токенов после смены пароля
    token_pwd_reset_at = payload.get("pwd_reset_at")
    if token_pwd_reset_at:
        token_pwd_reset_at = datetime.fromtimestamp(token_pwd_reset_at).replace(microsecond=0)

        if user.last_password_reset:
            user_pwd_reset_at = user.last_password_reset.replace(microsecond=0)
            if token_pwd_reset_at < user_pwd_reset_at:
                raise InvalidTokenException

    return user
