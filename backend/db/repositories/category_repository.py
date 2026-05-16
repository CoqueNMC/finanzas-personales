from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import Category, Transaction
from .base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_all_with_counts(self, user_id: str) -> list[dict]:
        rows = (
            self.db.query(Category, func.count(Transaction.id).label("tx_count"))
            .outerjoin(Transaction, Transaction.category_id == Category.id)
            .filter(Category.user_id == user_id)
            .group_by(
                Category.id, Category.name,
                Category.emoji, Category.color, Category.user_id
            )
            .order_by(Category.name)
            .all()
        )
        return [{"category": cat, "transaction_count": count} for cat, count in rows]

    def has_transactions(self, category_id: str) -> int:
        return self.db.query(func.count(Transaction.id)).filter(
            Transaction.category_id == category_id
        ).scalar() or 0
