# app/finance/transaction/schemas/responses.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    description: str | None
    occurred_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
