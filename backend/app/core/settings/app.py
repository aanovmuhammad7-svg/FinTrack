import logging
import sys
from typing import Any, Dict, Tuple, List
from loguru import logger
from pydantic import PostgresDsn, SecretStr

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings

class AppSettings(BaseAppSettings):
    debug: bool

    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FinTrack API"
    version: str = "0.1.0"

    database_url: PostgresDsn

    connection_count: int = 10
    additional_connections: int = 0

    secret_key: SecretStr
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 60  # 1 hour
    refresh_token_expire_days: int = 7  # 7 days

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    allowed_hosts: List[str] = ["*"]

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
