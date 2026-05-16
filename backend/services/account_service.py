from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.repositories import AccountRepository
from backend.models import Account
from backend.schemas import AccountCreate, AccountUpdate, AccountOut
from backend.services.id_service import generate_id
from backend.models import User

class AccountService:
    def __init__(self, db: Session, current_user: User):
        self.repo = AccountRepository(db)
        self.current_user = current_user

    def get_all(self) -> list[AccountOut]:
        rows = self.repo.get_all_with_balances(self.current_user.id)
        return [
            AccountOut(**{**vars(r["account"]), "current_balance": r["current_balance"]})
            for r in rows
        ]

    def get_by_id(self, account_id: str) -> AccountOut:
        row = self.repo.get_with_balance(account_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cuenta '{account_id}' no encontrada")
        return AccountOut(**{**vars(row["account"]), "current_balance": row["current_balance"]})

    def create(self, data: AccountCreate) -> AccountOut:
        account = Account(
            id=generate_id("acc"),
            user_id=self.current_user.id,
            **data.model_dump()
        )
        self.repo.create(account)
        return AccountOut(**{**vars(account), "current_balance": account.initial_balance})

    def update(self, account_id: str, data: AccountUpdate) -> AccountOut:
        account = self.repo.get_by_id(account_id)
        if not account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cuenta '{account_id}' no encontrada")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(account, field, value)
        balance = self.repo._calculate_balance(account_id)
        return AccountOut(**{**vars(account), "current_balance": balance})

    def delete(self, account_id: str) -> dict:
        if not self.repo.soft_delete(account_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cuenta '{account_id}' no encontrada")
        return {"message": "Cuenta desactivada", "id": account_id}
