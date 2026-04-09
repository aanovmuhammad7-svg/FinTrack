import os
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def pytest_configure() -> None:
    for env_name in (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "REDIS_PASSWORD",
    ):
        os.environ.pop(env_name, None)

    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("PASSWORD_VALIDATION_LEVEL", "light")
    os.environ.setdefault(
        "PASSWORDS_COMMON_LIST_PATH",
        str(BACKEND_ROOT / "app" / "auth" / "utils" / "common_passwords_list.txt"),
    )
    os.environ.setdefault("PASSWORD_BCRYPT_SALT_ROUNDS", "12")
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/fintrack")
    os.environ.setdefault("CONNECTION_COUNT", "5")
    os.environ.setdefault("ADDITIONAL_CONNECTIONS", "5")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("REDIS_MAX_CONNECTIONS", "10")
    os.environ.setdefault("ALLOWED_HOSTS", "http://localhost:3000,http://localhost:5173")
    os.environ.setdefault("JWT_ALGORITHM", "RS256")
    os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRE", "15")
    os.environ.setdefault("JWT_REFRESH_TOKEN_EXPIRE", "7")
    os.environ.setdefault("JWT_RESET_TOKEN_EXPIRE", "30")
    os.environ.setdefault("JWT_PRIVATE_KEY_PATH", str(BACKEND_ROOT / "private.pem"))
    os.environ.setdefault("JWT_PUBLIC_KEY_PATH", str(BACKEND_ROOT / "public.pem"))
    os.environ.setdefault("COOKIE_SECURE", "false")
    os.environ.setdefault(
        "EMAIL_TEMPLATES_PATH",
        str(BACKEND_ROOT / "app" / "email" / "templates"),
    )
    os.environ.setdefault("ENABLE_EMAIL_CONFIRMATION", "true")
    os.environ.setdefault("EMAIL_CONFIRM_TOKEN_EXPIRE", "30")
    os.environ.setdefault("EMAIL_FROM", "noreply@example.com")
    os.environ.setdefault("SMTP_USERNAME", "user")
    os.environ.setdefault("SMTP_PASSWORD", "password")
    os.environ.setdefault("SMTP_HOST", "localhost")
    os.environ.setdefault("SMTP_PORT", "1025")
    os.environ.setdefault("ENABLE_RATE_LIMITER", "true")
