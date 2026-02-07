# app/finance/transactions/schemas/filters.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional

class TransactionFilter(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None
