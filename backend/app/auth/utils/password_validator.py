import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

from app.core.config import settings


class PasswordValidator:
    """
    Класс для валидации паролей на основе заданного уровня строгости.
    """
    VALID_LEVELS = {"none", "light", "medium", "strong"}

    def __init__(
        self,
        level: str = settings.password_validation_level,
        common_passwords_path: Optional[str] = settings.passwords_common_list_path,
    ):
        self.level = level.lower()
        if self.level not in self.VALID_LEVELS:
            raise ValueError(f"Недопустимый уровень проверки пароля: {self.level}")

        self._common_passwords: set[str] = set()

        if common_passwords_path:
            path = Path(common_passwords_path)
            if path.exists():
                try:
                    with path.open(encoding="utf-8") as f:
                        self._common_passwords = {
                            line.strip().lower()
                            for line in f
                            if line.strip()
                        }
                except Exception:
                    # сознательно без print / raise
                    self._common_passwords = set()

    def validate(self, password: str, email: Optional[str] = None) -> list[str]:
        """
        Возвращает список ошибок.
        Пустой список означает, что пароль валиден.
        """
        errors: list[str] = []

        if self.level == "none":
            if not password:
                errors.append("Пароль не может быть пустым")
            return errors

        errors += self._check_length(password)
        errors += self._check_characters(password)

        if self.level in ("medium", "strong"):
            if email:
                errors += self._check_similarity(password, email)
            errors += self._check_common_password(password)

        return errors

    def _check_length(self, password: str) -> list[str]:
        min_len = 8 if self.level == "light" else 10
        if len(password) < min_len:
            return [f"Пароль должен содержать минимум {min_len} символов"]
        return []

    def _check_characters(self, password: str) -> list[str]:
        errors: list[str] = []

        if not re.search(r"[A-Za-z]", password):
            errors.append("Пароль должен содержать хотя бы одну букву")
        if not re.search(r"\d", password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        if self.level in ("medium", "strong"):
            if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:\\|,.<>/?~]", password):
                errors.append("Пароль должен содержать хотя бы один спецсимвол")

        if self.level == "strong":
            if not re.search(r"[a-z]", password):
                errors.append("Пароль должен содержать хотя бы одну строчную букву")
            if not re.search(r"[A-Z]", password):
                errors.append("Пароль должен содержать хотя бы одну заглавную букву")

        return errors

    def _check_similarity(self, password: str, email: str) -> list[str]:
        errors: list[str] = []
        password = password.lower()
        email_part = email.split("@")[0].lower()

        if password == email_part:
            errors.append("Пароль не должен совпадать с email")
        elif email_part in password:
            errors.append("Пароль не должен содержать email")
        elif SequenceMatcher(None, email_part, password).ratio() > 0.7:
            errors.append("Пароль слишком похож на email")

        return errors

    def _check_common_password(self, password: str) -> list[str]:
        if password.lower() in self._common_passwords:
            return ["Пароль слишком распространён"]
        return []


validator = PasswordValidator()
