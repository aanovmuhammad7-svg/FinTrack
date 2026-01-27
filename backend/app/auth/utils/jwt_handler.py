from typing import TypedDict, NotRequired, cast, Dict, Any
from pathlib import Path
import jwt
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.api.errors.exceptions import InvalidTokenException, ExpiredTokenException


class JWTPayload(TypedDict):
    sub: str
    iat: int
    exp: int
    jti: str
    user_id: int
    pwd_reset_at: NotRequired[int]


class JWTHandler:
    def __init__(self) -> None:
        self.private_key: str = Path(settings.jwt_private_key_path).read_text()
        self.public_key: str = Path(settings.jwt_public_key_path).read_text()
        self.algorithm: str = settings.jwt_algorithm
        self.access_exp_minutes: int = settings.jwt_access_token_expire
        self.refresh_exp_days: int = settings.jwt_refresh_token_expire
        self.reset_token_exp = settings.jwt_reset_token_expire
        
    def create_access_token(
        self,
        *,
        user_id: int,
        email: str,
    ) -> str:
        payload = self._base_payload(
            email=email,
            expires_delta=timedelta(minutes=self.access_exp_minutes),
            user_id=user_id,
        )

        return jwt.encode(
            cast(dict[str, object], payload),
            self.private_key,
            algorithm=self.algorithm,
        )

    def create_refresh_token(
        self,
        *,
        user_id: int,
        email: str,
    ) -> tuple[str, str, int]:
        payload = self._base_payload(
            email=email,
            expires_delta=timedelta(days=self.refresh_exp_days),
            user_id=user_id,
        )

        token = jwt.encode(
            cast(dict[str, object], payload),
            self.private_key,
            algorithm=self.algorithm,
        )

        expires_in = payload["exp"] - payload["iat"]
        return token, payload["jti"], expires_in

    def create_reset_token(
    self,
    *,
    email: str,
    ) -> str:
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(minutes=self.reset_token_exp)

        payload: Dict[str, Any] = {
            "sub": email,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": str(uuid4()),
        }


        return jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm,
    )


    def decode(self, token: str) -> JWTPayload:
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
            )
            return cast(JWTPayload, payload)
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise InvalidTokenException

    def _base_payload(
        self,
        *,
        email: str,
        expires_delta: timedelta,
        user_id: int,
    ) -> JWTPayload:
        now = datetime.now(tz=timezone.utc)
        exp = now + expires_delta

        return {
            "sub": email,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": str(uuid4()),
            "user_id": user_id,
        }
    
jwt_handler = JWTHandler()