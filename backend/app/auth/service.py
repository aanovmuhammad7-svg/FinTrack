from uuid import uuid4
from datetime import datetime, timezone
from fastapi import BackgroundTasks
from typing import Optional
from loguru import logger
from urllib.parse import quote

from app.core.config import settings
from app.email.utils.email_handler import email_handler
from app.auth.utils.password_validator import validator
from app.auth.utils.password_handler import password_handler
from app.auth.utils.jwt_handler import jwt_handler
from app.auth.schemas.requests import UserCreateRequest
from app.auth.repository import UserRepository, RefreshTokenRepository
from app.api.errors.exceptions import (
    UserAlreadyExistsException,
    PasswordValidationErrorException,
    InvalidCredentialsException,
    EmailNotConfirmedException,
    InvalidTokenException,
    UserNotFoundException,
    InvalidPasswordResetTokenException,
    PasswordIdenticalToPreviousException,
)


class RegistrationService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def _send_confirmation_email(
        self,
        email: str,
        token: str,
    ) -> None:
        try:
            link = (
                f"{settings.allowed_hosts}/email/confirm"
                f"?email={quote(email)}&token={token}"
            )

            html = email_handler.render_template(
                "confirm_email.html",
                {"confirmation_link": link},
            )

            await email_handler.send_email(
                to=email,
                subject="Подтверждение регистрации",
                html_content=html,
            )
        except Exception as exc:
            logger.error(f"Ошибка отправки письма {email}: {exc}")

    async def register_user(
        self,
        user_data: UserCreateRequest,
        background_tasks: BackgroundTasks,
    ):
        if await self.user_repo.is_email_taken(user_data.email):
            raise UserAlreadyExistsException(user_data.email)

        errors = validator.validate(
            password=user_data.password,
            email=user_data.email,
        )
        if errors:
            raise PasswordValidationErrorException(errors)
        

        hashed_password = password_handler.hash_password(user_data.password)

        email_confirmed: bool = True
        email_confirmed_at: Optional[datetime] = None
        confirmation_token: Optional[str] = None
        confirmation_token_created_at: Optional[datetime] = None
        
        if settings.enable_email_confirmation:
            email_confirmed = False
            email_confirmed_at = None
            confirmation_token = str(uuid4())
            confirmation_token_created_at = datetime.now(timezone.utc)

        user = await self.user_repo.create_user(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            birthday=getattr(user_data, "birthday", None),
            email_confirmed=email_confirmed,
            email_confirmed_at= email_confirmed_at,
            confirmation_token=confirmation_token,
            confirmation_token_created_at=confirmation_token_created_at,
        )

        if settings.enable_email_confirmation:
            assert confirmation_token is not None
            background_tasks.add_task(
                self._send_confirmation_email,
                user.email,
                confirmation_token,
            )

        return user
    

class LoginService:
    def __init__(self, user_repo: UserRepository, refresh_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo

    async def login_user(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        if not password_handler.verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        if settings.enable_email_confirmation and not user.email_confirmed:
            raise EmailNotConfirmedException()

        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
        )

        refresh_token, jti, expires_in = jwt_handler.create_refresh_token(
            user_id=user.id,
            email=user.email,
        )

        await self.refresh_repo.save(
            jti=jti,
            user_id=user.id,
            expires_in=expires_in,
        )

        await self.user_repo.update_last_login(user.id)

        return access_token, refresh_token

class RefreshService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo

    async def refresh(self, refresh_token: str) -> str:
        payload = jwt_handler.decode(refresh_token)

        user_id = payload.get("user_id")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise InvalidTokenException

        if not await self.refresh_repo.exists(jti):
            raise InvalidTokenException

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(payload.get("sub"))

        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
        )

        return access_token


class LogoutService:
    def __init__(self, refresh_repo: RefreshTokenRepository):
        self.refresh_repo = refresh_repo

    async def logout(self, refresh_token: str):
        payload = jwt_handler.decode(refresh_token)
        jti = payload.get("jti")
        user_id = payload.get("user_id")

        if not jti or not user_id:
            raise InvalidTokenException

        await self.refresh_repo.delete(jti=jti, user_id=user_id)

class PasswordResetService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo

    async def forgot_password(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return

        token = jwt_handler.create_reset_token(email=user.email)

        await self.user_repo.update(
            user.id,
            {
                "password_reset_token": token,
                "password_reset_token_created_at": datetime.now(timezone.utc),
            },
        )

        try:
            link = f"{settings.allowed_hosts}/reset-password?token={token}"
            html = email_handler.render_template(
                "reset_password.html",
                {"reset_link": link},
            )
            await email_handler.send_email(
                to=user.email,
                subject="Сброс пароля",
                html_content=html,
            )
        except Exception as exc:
            logger.error(f"Ошибка отправки письма сброса пароля: {exc}")

    
    async def reset_password(self, token: str, new_password: str) -> None:
        payload = jwt_handler.decode(token)
        email = payload.get("sub")

        if not email:
            raise InvalidPasswordResetTokenException

        user = await self.user_repo.find_one_or_none(
            email=email,
            password_reset_token=token,
        )
        if not user:
            raise InvalidPasswordResetTokenException

        if password_handler.verify_password(new_password, user.hashed_password):
            raise PasswordIdenticalToPreviousException

        errors = validator.validate(password=new_password, email=user.email)
        if errors:
            raise PasswordValidationErrorException(errors)

        await self.user_repo.update(
            user.id,
            {
                "hashed_password": password_handler.hash_password(new_password),
                "password_reset_token": None,
                "password_reset_token_created_at": None,
                "last_password_reset": datetime.now(timezone.utc),
            },
        )

        await self.refresh_repo.delete_all_for_user(user.id)