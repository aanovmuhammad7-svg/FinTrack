from fastapi import APIRouter, status, Depends, Request
from app.api.dependencies.auth_dep import get_current_user
from app.users.schemas.responses import UserBaseResponse
from app.api.dependencies.limiter import limiter
from app.db.models.models import User


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/profile", response_model=UserBaseResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    ) -> UserBaseResponse:
    return UserBaseResponse.model_validate(current_user)