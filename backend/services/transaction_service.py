from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.repositories import TransactionRepository, AccountRepository
from backend.models import Transaction
from backend.schemas import TransactionCreate, TransactionUpdate, TransactionOut
from backend.schemas.transaction import TransactionFilter
from backend.services.id_service import generate_id
from backend.models import User

class TransactionService:
    def __init__(self, db: Session, current_user: User):
        self.repo = TransactionRepository(db, current_user)
        self.acc_repo = AccountRepository(db)
        self.current_user = current_user

    def get_filtered(self, filters: TransactionFilter) -> dict:
        items, total = self.repo.get_filtered(filters)
        return {
            "items": [self._to_out(t) for t in items],
            "total": total, "page": filters.page,
            "page_size": filters.page_size,
            "pages": max(1, -(-total // filters.page_size)),
        }

    def create(self, data: TransactionCreate) -> TransactionOut:
        self._validate_accounts(data)
        tx = Transaction(
            id=generate_id("tx"),
            user_id=self.current_user.id,
            **data.model_dump()
        )
        self.repo.create(tx)
        tx = self.repo.get_by_id(tx.id)
        return self._to_out(tx)

    def update(self, tx_id: str, data: TransactionUpdate) -> TransactionOut:
        tx = self.repo.get_by_id(tx_id)
        if not tx:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Transacción '{tx_id}' no encontrada")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(tx, field, value)
        return self._to_out(tx)

    def delete(self, tx_id: str) -> dict:
        if not self.repo.delete(tx_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Transacción '{tx_id}' no encontrada")
        return {"message": "Transacción eliminada", "id": tx_id}

    def get_dashboard_summary(self, year_month: str) -> dict:
        return self.repo.get_summary_by_month(year_month)

    def get_expense_by_category(self, year_month: str = None) -> list:
        return self.repo.get_expense_by_category(year_month)

    def _validate_accounts(self, data: TransactionCreate):
        if data.account_id and not self.acc_repo.exists(data.account_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cuenta '{data.account_id}' no existe")
        if data.to_account_id and not self.acc_repo.exists(data.to_account_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cuenta destino no existe")

    def _to_out(self, tx: Transaction) -> TransactionOut:
        return TransactionOut(
            id=tx.id, description=tx.description, amount=tx.amount,
            date=tx.date, type=tx.type, account_id=tx.account_id,
            to_account_id=tx.to_account_id, category_id=tx.category_id,
            account_name=tx.account.name if tx.account else None,
            account_emoji=tx.account.emoji if tx.account else None,
            category_name=tx.category.name if tx.category else None,
            category_emoji=tx.category.emoji if tx.category else None,
            category_color=tx.category.color if tx.category else None,
            created_at=tx.created_at.isoformat() if tx.created_at else None,
        )
