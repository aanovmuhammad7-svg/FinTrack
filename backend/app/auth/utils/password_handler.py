import bcrypt
from app.core.config import settings


class PasswordHandler:
    def __init__(self, salt_rounds: int):
        self.salt_rounds = salt_rounds

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        return bcrypt.hashpw(
            password.encode("utf-8"),
            salt
        ).decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )


password_handler = PasswordHandler(
    salt_rounds=settings.password_bcrypt_salt_rounds
)
