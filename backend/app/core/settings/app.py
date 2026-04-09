import logging
import sys
from typing import Any, Dict, Literal, Tuple

from loguru import logger
from pydantic import PostgresDsn, RedisDsn, field_validator

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    environment: Literal["development", "staging", "production", "test"] = "development"

    # Password validation
    password_validation_level: Literal["none", "light", "medium", "strong"]
    passwords_common_list_path: str
    password_bcrypt_salt_rounds: int

    # FastAPI settings
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FinTrack API"
    version: str = "0.1.0"

    # PostgreSQL
    database_url: PostgresDsn
    connection_count: int
    additional_connections: int

    # Redis
    redis_url: RedisDsn
    redis_max_connections: int

    # Logging
    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    # Frontend
    allowed_hosts: list[str] | str = ["http://localhost:3000"]

    # JWT
    jwt_algorithm: str
    jwt_access_token_expire: int
    jwt_refresh_token_expire: int
    jwt_reset_token_expire: int
    jwt_private_key_path: str
    jwt_public_key_path: str
    cookie_secure: bool

    # Email
    email_templates_path: str
    enable_email_confirmation: bool
    email_confirm_token_expire: int

    # SMTP
    email_from: str
    smtp_username: str
    smtp_password: str
    smtp_host: str
    smtp_port: int

    # Rate limiting
    enable_rate_limiter: bool

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: object) -> list[str]:
        if value is None:
            return ["http://localhost:3000"]

        if isinstance(value, str):
            hosts = [item.strip() for item in value.split(",") if item.strip()]
            return hosts or ["http://localhost:3000"]

        if isinstance(value, (list, tuple)):
            hosts = [str(item).strip() for item in value if str(item).strip()]
            return hosts or ["http://localhost:3000"]

        raise ValueError("allowed_hosts must be a string or list of strings")

    @field_validator("environment", mode="before")
    @classmethod
    def parse_environment(cls, value: object) -> str:
        if value is None:
            return "development"

        normalized = str(value).strip().lower()
        aliases = {
            "dev": "development",
            "development": "development",
            "local": "development",
            "stage": "staging",
            "staging": "staging",
            "prod": "production",
            "production": "production",
            "release": "production",
            "test": "test",
            "testing": "test",
        }
        if normalized not in aliases:
            raise ValueError("environment must be one of development, staging, production, test")
        return aliases[normalized]

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False

        normalized = str(value).strip().lower()
        truthy = {"1", "true", "yes", "on", "debug"}
        falsy = {"0", "false", "no", "off", "release", "prod", "production"}

        if normalized in truthy:
            return True
        if normalized in falsy:
            return False

        raise ValueError("debug must be a boolean-like value")

    @property
    def frontend_url(self) -> str:
        return self.allowed_hosts[0]

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]

        for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
            uvicorn_logger = logging.getLogger(logger_name)
            uvicorn_logger.handlers = [InterceptHandler()]
            uvicorn_logger.propagate = False

        logger.remove()
        logger.add(
            sys.stdout,
            colorize=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level:<8}</level> | "
                "<cyan>{name}</cyan>:<green>{function}</green>:<yellow>{line}</yellow> - "
                "<level>{message}</level>"
            ),
            level=self.logging_level,
        )
