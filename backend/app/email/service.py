from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import uuid4

from loguru import logger

from app.api.errors.exceptions import (
    EmailAlreadyConfirmedException,
    InvalidOrExpiredEmailTokenException,
    TooEarlyResendException,
)
from app.auth.repository import UserRepository
from app.core.config import settings
from app.db.models.models import User
from app.email.utils.email_handler import email_handler


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
            minutes=settings.email_confirm_token_expire
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
            logger.error(f"Failed to confirm email for {email}: user update returned no result")
            raise InvalidOrExpiredEmailTokenException()

        logger.info(f"Email for user {email} was confirmed successfully")


class ResendConfirmationService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def resend_confirmation(self, user: User) -> None:
        if user.email_confirmed:
            raise EmailAlreadyConfirmedException

        created_at = user.confirmation_token_created_at
        if created_at and datetime.now(timezone.utc) - created_at < timedelta(
            minutes=settings.email_confirm_token_expire
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
            link = (
                f"{settings.frontend_url}/email/confirm"
                f"?email={quote(user.email)}&token={new_token}"
            )
            html_content = email_handler.render_template(
                "confirm_email.html",
                {"confirmation_link": link},
            )
            await email_handler.send_email(
                to=user.email,
                subject="Confirm your registration",
                html_content=html_content,
            )
        except Exception as exc:
            logger.error(
                f"Failed to send confirmation email to {user.email}: {type(exc).__name__}: {exc}"
            )
