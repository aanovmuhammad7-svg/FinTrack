from uuid import uuid4
from datetime import datetime, timedelta, timezone
from loguru import logger

from app.db.models.models import User
from app.core.config import settings
from app.auth.repository import UserRepository
from app.email.utils.email_handler import email_handler
from app.api.errors.exceptions import (
    TooEarlyResendException,
    EmailAlreadyConfirmedException,
    InvalidOrExpiredEmailTokenException,
)


class ConfirmyEmailService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def confirm_email(self, email: str, token: str) -> None:
        user = await self.user_repo.find_one_or_none(
            email=email,
            confirmation_token=token,
        )

        if not user or user.email_confirmed:
            raise InvalidOrExpiredEmailTokenException

        created_at = user.confirmation_token_created_at
        if not created_at or datetime.now(timezone.utc) - created_at > timedelta(
            hours=settings.email_confirm_token_expire
        ):
            raise InvalidOrExpiredEmailTokenException

        updated_user = await self.user_repo.update(
            user.id,
            {
                "email_confirmed": True,
                "email_confirmed_at": datetime.now(timezone.utc),
                "confirmation_token": None,
                "confirmation_token_created_at": None,
            },
        )

        if not updated_user:
            logger.error(
                f"Ошибка при подтверждении email: не удалось обновить пользователя с email {email}"
            )
            raise InvalidOrExpiredEmailTokenException()

        logger.info(f"Email пользователя {email} успешно подтверждён", extra={"log_info": True})

class ResendConfirmationService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def resend_confirmation(self, user: User) -> None:
        if user.email_confirmed:
            raise EmailAlreadyConfirmedException

        created_at = user.confirmation_token_created_at
        if created_at and datetime.now(timezone.utc) - created_at < timedelta(
            hours=settings.email_confirm_token_expire
        ):
            raise TooEarlyResendException

        new_token = str(uuid4())
        created_at = datetime.now(timezone.utc)
        await self.user_repo.update(
            user.id,
            {
                "confirmation_token": new_token,
                "confirmation_token_created_at": created_at,
            },
        )

        try:
            link = f"{settings.allowed_hosts}/email/confirm?email={user.email}&token={new_token}"
            html_content = email_handler.render_template(
                "confirm_email.html",
                {"confirmation_link": link}
            )
            await email_handler.send_email(
                to=user.email,
                subject="Подтверждение регистрации",
                html_content=html_content,
            )
        except Exception as e:
            logger.error(
                f"Ошибка отправки email для подтверждения ({user.email}): {type(e).__name__}: {e}"
            )
