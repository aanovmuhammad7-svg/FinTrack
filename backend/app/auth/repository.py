from app.db.models.models import User
from app.db.repository import BaseRepository
from datetime import datetime, timezone, date

from typing import Optional, cast, Any
from redis.asyncio import Redis


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.find_one_or_none(email=email)

    async def is_email_taken(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def create_user(
        self,
        *,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        birthday: date | None,
        email_confirmed: bool,
        email_confirmed_at: datetime | None,
        confirmation_token: str | None,
        confirmation_token_created_at: datetime | None,
    ) -> User:
        data: dict[str, Any] = {
            "email": email,
            "hashed_password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "birthday": birthday,
            "email_confirmed": email_confirmed,
            "email_confirmed_at": email_confirmed_at,
            "confirmation_token": confirmation_token,
            "confirmation_token_created_at": confirmation_token_created_at,
        }

        return await self.add(data)

    async def activate_user(self, user_id: int) -> Optional[User]:
        return await self.update(
            user_id,
            {"is_active": True}
        )

    async def confirm_email(
        self,
        user_id: int,
    ) -> Optional[User]:
        return await self.update(
            user_id,
            {
            "email_confirmed": True,
            "email_confirmed_at": datetime.now(timezone.utc),
            "confirmation_token": None,
            "confirmation_token_created_at": None,
            }
        )
    
    async def set_password_reset_token(
    self,
    user_id: int,
    token: str,
    ) -> Optional[User]:
        return await self.update(
            user_id,
            {
                "password_reset_token": token,
                "password_reset_token_created_at": datetime.now(timezone.utc),
            }
        )
    
    async def update_last_login(self, user_id: int) -> None:
        await self.update(
            user_id,
            {"last_login_at": datetime.now(timezone.utc)}
        )



class RefreshTokenRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _refresh_key(jti: str) -> str:
        return f"refresh:{jti}"

    @staticmethod
    def _user_key(user_id: int) -> str:
        return f"user_refresh:{user_id}"

    async def save(
        self,
        *,
        jti: str,
        user_id: int,
        expires_in: int,
    ) -> None:
        pipe = self.redis.pipeline()

        pipe.set(
            self._refresh_key(jti),
            user_id,
            ex=expires_in,
        )

        pipe.sadd(self._user_key(user_id), jti)
        pipe.expire(self._user_key(user_id), expires_in)

        await pipe.execute()

    async def get_user_id(self, jti: str) -> Optional[int]:
        value = await self.redis.get(self._refresh_key(jti))
        return int(value) if value else None

    async def delete(self, *, jti: str, user_id: int) -> None:
        pipe = self.redis.pipeline()
        pipe.delete(self._refresh_key(jti))
        pipe.srem(self._user_key(user_id), jti)
        await pipe.execute()

    async def delete_all_for_user(self, user_id: int) -> None:
        key = self._user_key(user_id)
        jtis = cast(set[str], await self.redis.smembers(key)) # type: ignore

        if not jtis:
            return

        pipe = self.redis.pipeline()
        for jti in jtis:
            pipe.delete(self._refresh_key(jti))

        pipe.delete(key)
        await pipe.execute()

    async def exists(self, jti: str) -> bool:
        return await self.redis.exists(self._refresh_key(jti)) == 1