from fastapi.responses import JSONResponse

from app.auth.utils.cookie_handler import CookieHandler


def test_set_auth_tokens_sets_access_refresh_and_csrf_cookies() -> None:
    response = JSONResponse({"ok": True})
    handler = CookieHandler(access_token_expire=15, refresh_token_expire=7)

    csrf_value = handler.set_auth_tokens(
        response=response,
        access_token="access-token",
        refresh_token="refresh-token",
        csrf_token="csrf-fixed",
    )

    set_cookie_headers = "\n".join(
        value.decode("latin-1")
        for key, value in response.raw_headers
        if key.lower() == b"set-cookie"
    )

    assert csrf_value == "csrf-fixed"
    assert "access_token=access-token" in set_cookie_headers
    assert "refresh_token=refresh-token" in set_cookie_headers
    assert "csrf_token=csrf-fixed" in set_cookie_headers
    assert "HttpOnly" in set_cookie_headers
    assert "Path=/auth" in set_cookie_headers


def test_clear_auth_tokens_marks_all_auth_cookies_for_deletion() -> None:
    response = JSONResponse({"ok": True})

    CookieHandler.clear_auth_tokens(response)

    set_cookie_headers = "\n".join(
        value.decode("latin-1")
        for key, value in response.raw_headers
        if key.lower() == b"set-cookie"
    )

    assert "access_token=\"\"" in set_cookie_headers
    assert "refresh_token=\"\"" in set_cookie_headers
    assert "csrf_token=\"\"" in set_cookie_headers
