from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from backend.models import Transaction, Account, Category
from backend.schemas.transaction import TransactionFilter
from .base_repository import BaseRepository
from typing import Optional


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session, current_user=None):
        super().__init__(Transaction, db)
        self.current_user = current_user

    def get_filtered(self, filters: TransactionFilter) -> tuple[list[Transaction], int]:
        query = (
            self.db.query(Transaction)
            .options(
                joinedload(Transaction.account),
                joinedload(Transaction.category),
            )
        )
        if self.current_user:
            query = query.filter(Transaction.user_id == self.current_user.id)

        conditions = self._build_conditions(filters)
        if conditions:
            query = query.filter(and_(*conditions))

        total = query.count()
        offset = (filters.page - 1) * filters.page_size
        items = (
            query
            .order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .offset(offset)
            .limit(filters.page_size)
            .all()
        )
        return items, total

    def _build_conditions(self, filters) -> list:
        conditions = []
        if filters.search:
            conditions.append(Transaction.description.ilike(f"%{filters.search}%"))
        if filters.type:
            conditions.append(Transaction.type == filters.type)
        if filters.account_id:
            conditions.append(Transaction.account_id == filters.account_id)
        if filters.category_id:
            conditions.append(Transaction.category_id == filters.category_id)
        if filters.date_from:
            conditions.append(Transaction.date >= filters.date_from)
        if filters.date_to:
            conditions.append(Transaction.date <= filters.date_to)
        return conditions

    def get_summary_by_month(self, year_month: str) -> dict:
        from backend.models.transaction import TransactionType
        from sqlalchemy import extract
        
        year, month = year_month.split("-")
        
        query = self.db.query(
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        ).filter(
            extract("year", Transaction.date) == int(year),
            extract("month", Transaction.date) == int(month),
        )

        if self.current_user:
            query = query.filter(Transaction.user_id == self.current_user.id)

        rows = query.group_by(Transaction.type).all()
        summary = {t.value: {"total": 0.0, "count": 0} for t in TransactionType}
        for row in rows:
            summary[row.type.value] = {"total": float(row.total), "count": row.count}
        return summary

    def get_expense_by_category(self, year_month: Optional[str] = None) -> list[dict]:
        from backend.models.transaction import TransactionType
        from sqlalchemy import extract

        query = (
            self.db.query(
                Category.id, Category.name, Category.emoji,
                Category.color, func.sum(Transaction.amount).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(Transaction.type.in_([TransactionType.expense, TransactionType.expense_tc]))
        )
        if self.current_user:
            query = query.filter(Transaction.user_id == self.current_user.id)
        if year_month:
            year, month = year_month.split("-")
            query = query.filter(
                extract("year", Transaction.date) == int(year),
                extract("month", Transaction.date) == int(month),
            )
        rows = query.group_by(
            Category.id, Category.name, Category.emoji, Category.color
        ).order_by(func.sum(Transaction.amount).desc()).all()
        return [
            {"id": r.id, "name": r.name, "emoji": r.emoji, "color": r.color, "total": float(r.total)}
            for r in rows
        ]

    def bulk_insert(self, transactions: list[Transaction]) -> int:
        """Inserción masiva eficiente para migración de datos."""
        self.db.bulk_save_objects(transactions)
        self.db.flush()
        return len(transactions)

    def get_expense_by_category_range(self, date_from=None, date_to=None) -> list[dict]:
        from backend.models.transaction import TransactionType
        query = (
            self.db.query(
                Category.id, Category.name, Category.emoji,
                Category.color, func.sum(Transaction.amount).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(Transaction.type.in_([TransactionType.expense, TransactionType.expense_tc]))
        )
        if self.current_user:
            query = query.filter(Transaction.user_id == self.current_user.id)
        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)
        rows = query.group_by(
            Category.id, Category.name, Category.emoji, Category.color
        ).order_by(func.sum(Transaction.amount).desc()).all()
        return [
            {"id": r.id, "name": r.name, "emoji": r.emoji, "color": r.color, "total": float(r.total)}
            for r in rows
        ]