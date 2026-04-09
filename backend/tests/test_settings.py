from app.core.settings.app import AppSettings


BASE_SETTINGS = {
    "password_validation_level": "light",
    "passwords_common_list_path": "app/auth/utils/common_passwords_list.txt",
    "password_bcrypt_salt_rounds": 12,
    "database_url": "postgresql+asyncpg://user:pass@localhost:5432/fintrack",
    "connection_count": 5,
    "additional_connections": 5,
    "redis_url": "redis://localhost:6379/0",
    "redis_max_connections": 10,
    "jwt_algorithm": "RS256",
    "jwt_access_token_expire": 15,
    "jwt_refresh_token_expire": 7,
    "jwt_reset_token_expire": 30,
    "jwt_private_key_path": "private.pem",
    "jwt_public_key_path": "public.pem",
    "cookie_secure": False,
    "email_templates_path": "app/email/templates",
    "enable_email_confirmation": True,
    "email_confirm_token_expire": 30,
    "email_from": "noreply@example.com",
    "smtp_username": "user",
    "smtp_password": "password",
    "smtp_host": "localhost",
    "smtp_port": 1025,
    "enable_rate_limiter": True,
}


def build_settings(**overrides: object) -> AppSettings:
    return AppSettings(**(BASE_SETTINGS | overrides))


def test_environment_alias_release_maps_to_production() -> None:
    settings = build_settings(environment="release")

    assert settings.environment == "production"


def test_debug_aliases_map_to_boolean_values() -> None:
    assert build_settings(debug="debug").debug is True
    assert build_settings(debug="release").debug is False


def test_allowed_hosts_string_is_parsed_to_list() -> None:
    settings = build_settings(
        allowed_hosts="http://localhost:3000, https://app.example.com"
    )

    assert settings.allowed_hosts == [
        "http://localhost:3000",
        "https://app.example.com",
    ]
    assert settings.frontend_url == "http://localhost:3000"
