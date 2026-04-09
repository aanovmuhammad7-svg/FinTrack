from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.limiter import limiter
from app.auth.repository import UserRepository
from app.db.database import get_async_session
from app.email.schemas.requests import EmailConfirmationRequest, EmailResendRequest
from app.email.schemas.responses import MessageResponse
from app.email.service import ConfirmyEmailService, ResendConfirmationService


router = APIRouter(prefix="/email", tags=["Email"])


@router.post(
    "/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm email",
)
@limiter.limit("10/minute")
async def confirm_email(
    request: Request,
    data: EmailConfirmationRequest,
    session: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(session)
    service = ConfirmyEmailService(user_repo)

    await service.confirm_email(email=data.email, token=str(data.confirmation_token))
    return MessageResponse(message="Email was confirmed successfully")


@router.post(
    "/resend",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend confirmation email",
)
@limiter.limit("3/15minute")
async def resend_confirmation(
    request: Request,
    data: EmailResendRequest,
    session: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(session)
    service = ResendConfirmationService(user_repo)
    user = await user_repo.get_by_email(data.email)

    if user and not user.email_confirmed:
        await service.resend_confirmation(user)

    return MessageResponse(message="If the account exists, the confirmation email was sent again")
