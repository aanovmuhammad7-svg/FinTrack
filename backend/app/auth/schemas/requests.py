from datetime import date
from pydantic import BaseModel, EmailStr


class UserBaseRequest(BaseModel):
    email: EmailStr


class UserCreateRequest(UserBaseRequest):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    birthday: date


class LoginRequest(UserBaseRequest):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
