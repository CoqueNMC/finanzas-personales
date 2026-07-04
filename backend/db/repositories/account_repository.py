from sqlalchemy.orm import Session
from sqlalchemy import func, case
from backend.models import Account, Transaction
from backend.models.transaction import TransactionType
from .base_repository import BaseRepository
from typing import Optional


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: Session):
        super().__init__(Account, db)

    def get_all(self, user_id: str) -> list[Account]:
        return self.db.query(self.model).filter(
            self.model.is_active == True,
            self.model.user_id == user_id
        ).all()

    def get_with_balance(self, account_id: str) -> Optional[dict]:
        """Retorna la cuenta con su saldo calculado desde las transacciones."""
        account = self.get_by_id(account_id)
        if not account:
            return None
        balance = self._calculate_balance(account_id)
        return {"account": account, "current_balance": balance}

    def get_all_with_balances(self, user_id: str) -> list[dict]:
        accounts = self.get_all(user_id)
        return [
            {"account": a, "current_balance": self._calculate_balance(a.id)}
            for a in accounts
        ]

    def _calculate_balance(self, account_id: str) -> float:
        """
        Calcula el saldo de una cuenta sumando todas sus transacciones.
        Esta lógica vive en el repositorio para que el servicio no necesite SQL.
        """
        account = self.get_by_id(account_id)
        initial = account.initial_balance if account else 0.0

        result = self.db.query(
            func.coalesce(func.sum(
                case(
                    (Transaction.type == TransactionType.income, Transaction.amount),
                    (
                        Transaction.type.in_([
                            TransactionType.transfer,
                            TransactionType.invest,
                            TransactionType.withdraw,
                            TransactionType.move,
                        ]) & (Transaction.to_account_id == account_id),
                        Transaction.amount,
                    ),
                    else_=0.0,
                )
            ), 0.0) -
            func.coalesce(func.sum(
                case(
                    (
                        Transaction.type.in_([
                            TransactionType.expense,
                            TransactionType.expense_tc,
                        ]) & (Transaction.account_id == account_id),
                        Transaction.amount,
                    ),
                    (
                        Transaction.type.in_([
                            TransactionType.transfer,
                            TransactionType.invest,
                            TransactionType.withdraw,
                            TransactionType.move,
                        ]) & (Transaction.account_id == account_id),
                        Transaction.amount,
                    ),
                    else_=0.0,
                )
            ), 0.0)).filter(
            (Transaction.account_id == account_id) |
            (Transaction.to_account_id == account_id)
        ).scalar()

        return float(initial) + float(result or 0)

    def has_transactions(self, account_id: str) -> int:
            return self.db.query(func.count(Transaction.id)).filter(
                (Transaction.account_id == account_id) |
                (Transaction.to_account_id == account_id)
            ).scalar() or 0

    def soft_delete(self, account_id: str) -> bool:
        account = self.get_by_id(account_id)
        if not account:
            return False
        account.is_active = False
        self.db.flush()
        return True
