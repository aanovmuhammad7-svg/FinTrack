from uuid import UUID

from pydantic import BaseModel, EmailStr


class EmailConfirmationRequest(BaseModel):
    email: EmailStr
    confirmation_token: UUID


class EmailResendRequest(BaseModel):
    email: EmailStr
