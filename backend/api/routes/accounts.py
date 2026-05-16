from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.connection import get_db
from backend.schemas import AccountCreate, AccountUpdate, AccountOut
from backend.services import AccountService
from backend.core.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/accounts", tags=["Cuentas"])

def get_service(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AccountService(db, current_user)

@router.get("/", response_model=list[AccountOut])
def list_accounts(svc: AccountService = Depends(get_service)):
    return svc.get_all()

@router.get("/{account_id}/", response_model=AccountOut)
def get_account(account_id: str, svc: AccountService = Depends(get_service)):
    return svc.get_by_id(account_id)

@router.post("/", response_model=AccountOut, status_code=201)
def create_account(data: AccountCreate, svc: AccountService = Depends(get_service)):
    return svc.create(data)

@router.patch("/{account_id}/", response_model=AccountOut)
def update_account(account_id: str, data: AccountUpdate, svc: AccountService = Depends(get_service)):
    return svc.update(account_id, data)

@router.delete("/{account_id}/")
def delete_account(account_id: str, svc: AccountService = Depends(get_service)):
    return svc.delete(account_id)