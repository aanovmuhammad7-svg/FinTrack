from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    type: str
    description: str | None
    occurred_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True
