import base64
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    b64_password = base64.b64encode(password_bytes).decode("utf-8")
    return pwd_context.hash(b64_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    b64_password = base64.b64encode(password_bytes).decode("utf-8")
    return pwd_context.verify(b64_password, hashed_password)
