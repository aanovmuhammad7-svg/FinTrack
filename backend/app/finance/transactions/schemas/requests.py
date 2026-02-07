# app/finance/transaction/schemas/requests.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class TransactionCreate(BaseModel):
    category_id: int
    amount: Decimal
    description: str | None = None
    occurred_at: datetime | None = None


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = None
    description: str | None = None
    occurred_at: datetime | None = None
