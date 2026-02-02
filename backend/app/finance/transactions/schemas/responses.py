from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    description: str | None
    occurred_at: datetime
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)
