from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Any

from app.core.config import settings


ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key.get_secret_value()


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        ALGORITHM,
    )

    return encoded_jwt
