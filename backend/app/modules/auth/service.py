from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schema import RegisterRequest, LoginRequest
from app.modules.users.schema import UserCreate
from app.modules.users.service import get_user_by_email, create_user
from app.core.security.hashing import verify_password
from app.core.security.tokens import create_access_token


async def register_user(session: AsyncSession, data: RegisterRequest):
    if await get_user_by_email(session, data.email):
        raise ValueError("User with this email already exists")

    user = await create_user(
        session,
        UserCreate(
            email=data.email,
            username=data.username,
            password=data.password,
        ),
    )

    token = create_access_token(subject=str(user.id))
    return token


async def authenticate_user(session: AsyncSession, data: LoginRequest):
    user = await get_user_by_email(session, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise ValueError("Invalid email or password")

    token = create_access_token(subject=str(user.id))
    return token
