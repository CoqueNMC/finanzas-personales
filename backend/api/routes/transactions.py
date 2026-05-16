from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from backend.db.connection import get_db
from backend.schemas import TransactionCreate, TransactionUpdate, TransactionOut
from backend.schemas.transaction import TransactionFilter
from backend.services import TransactionService
from backend.core.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/transactions", tags=["Transacciones"])

def get_service(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TransactionService(db, current_user)

@router.get("/")
def list_transactions(
    search: Optional[str] = None,
    type: Optional[str] = None,
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    svc: TransactionService = Depends(get_service),
):
    filters = TransactionFilter(
        search=search, type=type, account_id=account_id,
        category_id=category_id, date_from=date_from,
        date_to=date_to, page=page, page_size=page_size
    )
    return svc.get_filtered(filters)

@router.get("/{tx_id}/", response_model=TransactionOut)
def get_transaction(tx_id: str, svc: TransactionService = Depends(get_service)):
    tx = svc.repo.get_by_id(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return svc._to_out(tx)

@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(data: TransactionCreate, svc: TransactionService = Depends(get_service)):
    return svc.create(data)

@router.patch("/{tx_id}/", response_model=TransactionOut)
def update_transaction(tx_id: str, data: TransactionUpdate, svc: TransactionService = Depends(get_service)):
    return svc.update(tx_id, data)

@router.delete("/{tx_id}/")
def delete_transaction(tx_id: str, svc: TransactionService = Depends(get_service)):
    return svc.delete(tx_id)