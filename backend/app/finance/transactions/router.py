# app/finance/transactions/router.py
from typing import List

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.dependencies.auth_dep import get_current_user, verify_csrf
from app.api.dependencies.limiter import limiter
from app.api.dependencies.transaction_dep import get_transaction_service
from app.db.models.models import User
from app.finance.transactions.schemas.filters import TransactionFilter
from app.finance.transactions.schemas.requests import TransactionCreate, TransactionUpdate
from app.finance.transactions.schemas.responses import TransactionResponse
from app.finance.transactions.service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Create transaction")
@limiter.limit("60/minute")
async def create_transaction(
    request: Request,
    data: TransactionCreate,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.create(user_id=current_user.id, data=data)


@router.get("/", response_model=List[TransactionResponse], summary="List transactions")
@limiter.limit("120/minute")
async def list_transactions(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.list(user_id=current_user.id)


@router.get("/filtered", response_model=List[TransactionResponse], summary="Filter transactions")
@limiter.limit("120/minute")
async def list_transactions_filtered(
    request: Request,
    filters: TransactionFilter = Depends(),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.list_filtered(
        user_id=current_user.id,
        filters=filters,
        limit=limit,
        offset=offset,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse, summary="Get transaction by id")
@limiter.limit("120/minute")
async def get_transaction(
    request: Request,
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.get_by_id(
        user_id=current_user.id,
        transaction_id=transaction_id,
    )


@router.patch("/{transaction_id}", response_model=TransactionResponse, summary="Update transaction")
@limiter.limit("60/minute")
async def update_transaction(
    request: Request,
    transaction_id: int,
    data: TransactionUpdate,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.update(
        user_id=current_user.id,
        transaction_id=transaction_id,
        data=data,
    )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete transaction")
@limiter.limit("60/minute")
async def delete_transaction(
    request: Request,
    transaction_id: int,
    _: None = Depends(verify_csrf),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    await service.delete(
        user_id=current_user.id,
        transaction_id=transaction_id,
    )
