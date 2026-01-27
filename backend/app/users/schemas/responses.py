from datetime import datetime, date
from pydantic import BaseModel, EmailStr


class UserBaseResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    birthday: date
    email_confirmed: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

