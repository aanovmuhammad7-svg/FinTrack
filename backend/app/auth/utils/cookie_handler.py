from fastapi.responses import JSONResponse
from app.core.config import settings


class CookieHandler:
    def __init__(self, access_token_expire: int = settings.jwt_access_token_expire,
        refresh_token_expire: int = settings.jwt_refresh_token_expire,
        ):
        self.access_token_expire = access_token_expire
        self.refresh_token_expire = refresh_token_expire

    def set_auth_tokens(self, response: JSONResponse, access_token: str, refresh_token: str) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            max_age=self.access_token_expire * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            max_age=self.refresh_token_expire * 60 * 60 * 24,
        )

    @staticmethod
    def clear_auth_tokens(response: JSONResponse):
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

cookie_handler = CookieHandler()