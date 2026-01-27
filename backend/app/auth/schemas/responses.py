from pydantic import BaseModel, EmailStr


class MessageResponse(BaseModel):
    message: str

class RefreshTokenResponse(MessageResponse):
    user: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"