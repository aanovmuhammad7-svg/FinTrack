from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate
from app.core.security.hashing import hash_password


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    user_data: UserCreate,
) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def update_user(
    session: AsyncSession,
    user: User,
    user_data: UserUpdate,
) -> User:
    if user_data.email is not None:
        user.email = user_data.email

    if user_data.password is not None:
        user.hashed_password = hash_password(user_data.password)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
