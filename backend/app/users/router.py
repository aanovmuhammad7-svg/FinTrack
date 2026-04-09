from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies.auth_dep import get_current_user
from app.api.dependencies.limiter import limiter
from app.db.models.models import User
from app.users.schemas.responses import UserBaseResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/profile",
    response_model=UserBaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
@limiter.limit("30/minute")
async def get_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> UserBaseResponse:
    return UserBaseResponse.model_validate(current_user)
