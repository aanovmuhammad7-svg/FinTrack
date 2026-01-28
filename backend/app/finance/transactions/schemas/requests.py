from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class TransactionCreate(BaseModel):
    category_id: int
    amount: Decimal
    type: str  # 'income' или 'expense'
    description: str | None = None
    occurred_at: datetime | None = None


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = None
    type: str | None = None
    description: str | None = None
    occurred_at: datetime | None = None
