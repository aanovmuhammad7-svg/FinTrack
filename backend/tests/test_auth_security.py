import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from starlette.requests import Request

from app.api.dependencies.auth_dep import (
    get_access_token,
    get_current_user,
    get_refresh_token,
    verify_csrf,
)
from app.api.errors.exceptions import (
    AccessTokenNotFoundException,
    CSRFMissingOrInvalidException,
    InvalidTokenException,
    RefreshTokenNotFoundException,
)


def build_request(*, cookie_header: str = "", csrf_header: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if cookie_header:
        headers.append((b"cookie", cookie_header.encode()))
    if csrf_header is not None:
        headers.append((b"x-csrf-token", csrf_header.encode()))
    return Request({"type": "http", "headers": headers})


def test_verify_csrf_accepts_matching_cookie_and_header() -> None:
    request = build_request(cookie_header="csrf_token=test-value", csrf_header="test-value")

    asyncio.run(verify_csrf(request))


def test_verify_csrf_rejects_missing_or_mismatched_token() -> None:
    request = build_request(cookie_header="csrf_token=test-value", csrf_header="wrong-value")

    with pytest.raises(CSRFMissingOrInvalidException):
        asyncio.run(verify_csrf(request))


def test_get_access_token_reads_cookie() -> None:
    request = build_request(cookie_header="access_token=access-123")

    token = asyncio.run(get_access_token(request))

    assert token == "access-123"


def test_get_access_token_raises_without_cookie() -> None:
    request = build_request()

    with pytest.raises(AccessTokenNotFoundException):
        asyncio.run(get_access_token(request))


def test_get_refresh_token_reads_cookie() -> None:
    request = build_request(cookie_header="refresh_token=refresh-123")

    token = asyncio.run(get_refresh_token(request))

    assert token == "refresh-123"


def test_get_refresh_token_raises_without_cookie() -> None:
    request = build_request()

    with pytest.raises(RefreshTokenNotFoundException):
        asyncio.run(get_refresh_token(request))


def test_get_current_user_rejects_token_issued_before_password_reset(monkeypatch) -> None:
    async def get_by_id(_: int):
        return SimpleNamespace(
            id=1,
            email="user@example.com",
            is_active=True,
            last_password_reset=datetime(2026, 4, 6, 12, 0, tzinfo=timezone.utc),
        )

    user_repo = SimpleNamespace(get_by_id=get_by_id)

    monkeypatch.setattr(
        "app.api.dependencies.auth_dep.jwt_handler.decode",
        lambda token, required_claims=None: {
            "sub": "user@example.com",
            "user_id": 1,
            "jti": "jti",
            "iat": 1,
            "exp": 2,
            "pwd_reset_at": 0,
        },
    )

    with pytest.raises(InvalidTokenException):
        asyncio.run(get_current_user(token="token", user_repo=user_repo))
