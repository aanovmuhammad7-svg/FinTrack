# app/finance/transactions/router.py
from fastapi import APIRouter, Depends, status
from typing import List

from app.api.dependencies.auth_dep import get_current_user
from app.db.models.models import User
from app.finance.transactions.schemas.requests import (
    TransactionCreate,
    TransactionUpdate,
)
from app.finance.transactions.schemas.responses import TransactionResponse
from app.finance.transactions.service import TransactionService
from app.api.dependencies.transaction_dep import get_transaction_service

router = APIRouter(prefix="/transactions", tags=["Транзакции"])


# --- CREATE ---
@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Создать транзакцию
    """
    return await service.create(user_id=current_user.id, data=data)


# --- LIST ---
@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Получить все транзакции пользователя
    """
    return await service.list(user_id=current_user.id)


# --- GET BY ID ---
@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Получить транзакцию по ID
    """
    return await service.get_by_id(
        user_id=current_user.id,
        transaction_id=transaction_id,
    )


# --- UPDATE ---
@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Обновить транзакцию
    """
    return await service.update(
        user_id=current_user.id,
        transaction_id=transaction_id,
        data=data,
    )


# --- DELETE ---
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Удалить транзакцию
    """
    await service.delete(
        user_id=current_user.id,
        transaction_id=transaction_id,
    )
