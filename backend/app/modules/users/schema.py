from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(min_length=5, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=30)

    class Config:
        extra = "forbid"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=5, max_length=30)
    password: Optional[str] = Field(default=None, min_length=8, max_length=30)

    class Config:
        extra = "forbid"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True