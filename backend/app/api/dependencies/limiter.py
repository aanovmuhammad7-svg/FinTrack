from typing import Any, Callable, Protocol, TypeVar

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

F = TypeVar("F", bound=Callable[..., Any])


class LimiterProtocol(Protocol):
    def limit(self, *args: Any, **kwargs: Any) -> Callable[[F], F]:
        ...


if settings.enable_rate_limiter:
    limiter: LimiterProtocol = Limiter(key_func=get_remote_address)
else:
    class DummyLimiter:
        def limit(self, *args: Any, **kwargs: Any) -> Callable[[F], F]:
            def decorator(func: F) -> F:
                return func

            return decorator

    limiter = DummyLimiter()


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please try again later."},
    )
