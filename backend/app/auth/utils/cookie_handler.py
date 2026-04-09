from fastapi.responses import JSONResponse
from app.core.config import settings
from secrets import token_urlsafe


class CookieHandler:
    def __init__(self, access_token_expire: int = settings.jwt_access_token_expire,
        refresh_token_expire: int = settings.jwt_refresh_token_expire,
        ):
        self.access_token_expire = access_token_expire
        self.refresh_token_expire = refresh_token_expire

    def set_auth_tokens(
        self,
        response: JSONResponse,
        access_token: str,
        refresh_token: str,
        csrf_token: str | None = None,
    ) -> str:
        csrf_value = csrf_token or token_urlsafe(32)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            path="/",
            max_age=self.access_token_expire * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            path="/auth",
            max_age=self.refresh_token_expire * 60 * 60 * 24,
        )
        response.set_cookie(
            key="csrf_token",
            value=csrf_value,
            httponly=False,
            secure=settings.cookie_secure,
            samesite="lax",
            path="/",
            max_age=self.refresh_token_expire * 60 * 60 * 24,
        )
        return csrf_value

    @staticmethod
    def clear_auth_tokens(response: JSONResponse):
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/auth")
        response.delete_cookie("csrf_token", path="/")

cookie_handler = CookieHandler()
