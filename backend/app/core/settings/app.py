import logging
import sys
from typing import Any, Dict, Tuple, Literal
from loguru import logger
from pydantic import PostgresDsn, RedisDsn

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings

class AppSettings(BaseAppSettings):

    # --- Пароли ---
    password_validation_level: Literal["none", "light", "medium", "strong"]  # Уровень строгости валидации паролей
    passwords_common_list_path: str  # Путь к файлу со списком часто используемых паролей
    password_bcrypt_salt_rounds: int # Количество раундов при генерации соли для шифрования пароля

    # --- Аргументы FastAPI ---
    debug: bool
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FinTrack API"
    version: str = "0.1.0"

    # --- Postgersql ---
    database_url: PostgresDsn
    connection_count: int
    additional_connections: int

    # --- Redis ---
    redis_url: RedisDsn
    redis_max_connections: int

    # --- Логгер ---
    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    # --- Frontend ---
    allowed_hosts: str = "http://localhost:3000"

    # --- JWT ---
    jwt_algorithm: str  # Алгоритм подписи JWT-токенов
    jwt_access_token_expire: int  # Время жизни access-токена (в минутах)
    jwt_refresh_token_expire: int  # Время жизни refresh-токена (в минутах)
    jwt_reset_token_expire: int  # Время жизни токена для сброса пароля (в минутах)
    jwt_private_key_path: str  # Путь к файлу с приватным ключом для JWT
    jwt_public_key_path: str  # Путь к файлу с публичным ключом для JWT
    cookie_secure: bool

    # --- Email ---
    email_templates_path: str  # Путь к шаблонам email-сообщений
    enable_email_confirmation: bool  # Включение подтверждения по email
    email_confirm_token_expire: int  # Время жизни токена подтверждения email (в минутах)

    # --- Email_Confirm_sistem ---
    email_from: str  # Адрес отправителя email
    smtp_username: str  # Имя пользователя для SMTP-сервера
    smtp_password: str  # Пароль для SMTP-сервера
    smtp_host: str  # Хост SMTP-сервера
    smtp_port: int  # Порт SMTP-сервера

    # --- Ограничения ---
    enable_rate_limiter: bool  # Включение ограничителя частоты запросов

    @property
    # --- Аргументы FastAPI ---
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

    # --- Конфигурации логгера ---
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