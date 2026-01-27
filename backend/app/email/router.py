from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import User
from app.db.database import get_async_session
from app.api.dependencies.limiter import limiter
from app.auth.repository import UserRepository
from app.api.dependencies.auth_dep import get_current_user
from app.api.dependencies.repo_dep import get_user_repository
from app.email.schemas.responses import MessageResponse
from app.email.schemas.requests import EmailConfirmationRequest
from app.email.service import ConfirmyEmailService, ResendConfirmationService
from app.api.errors.exceptions import UserNotFoundException


router = APIRouter(prefix="/email", tags=["Модуль работы с email"])


@router.post("/confirm", response_model=MessageResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def confirm_email(
    request: Request,
    data: EmailConfirmationRequest,
    session: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(session)
    service = ConfirmyEmailService(user_repo)

    await service.confirm_email(email=data.email, token=str(data.confirmation_token))
    return MessageResponse(message="Email успешно подтверждён")



@router.post("/resend", response_model=MessageResponse, status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def resend_confirmation(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
):
    service = ResendConfirmationService(user_repo)
    user = await user_repo.get_by_email(current_user.email)

    if not user:
        raise UserNotFoundException(current_user.email)

    await service.resend_confirmation(user)
    return MessageResponse(message="Если аккаунт существует, письмо отправлено повторно")