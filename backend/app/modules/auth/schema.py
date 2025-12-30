from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5, max_length=30)
    password: str = Field(min_length=8, max_length=30)

    class Config:
        extra = "forbid"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=30)

    class Config:
        extra = "forbid"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

