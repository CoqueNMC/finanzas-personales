from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.repositories import CategoryRepository
from backend.models import Category
from backend.schemas import CategoryCreate, CategoryUpdate, CategoryOut
from backend.services.id_service import generate_id
from backend.models import User

class CategoryService:
    def __init__(self, db: Session, current_user: User):
        self.repo = CategoryRepository(db)
        self.current_user = current_user

    def get_all(self) -> list[CategoryOut]:
        rows = self.repo.get_all_with_counts(self.current_user.id)
        return [
            CategoryOut(**{**vars(r["category"]), "transaction_count": r["transaction_count"]})
            for r in rows
        ]

    def create(self, data: CategoryCreate) -> CategoryOut:
        cat = Category(
            id=generate_id("cat"),
            user_id=self.current_user.id,
            **data.model_dump()
        )
        self.repo.create(cat)
        return CategoryOut(**{**vars(cat), "transaction_count": 0})

    def update(self, cat_id: str, data: CategoryUpdate) -> CategoryOut:
        cat = self.repo.get_by_id(cat_id)
        if not cat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Categoría '{cat_id}' no encontrada")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(cat, field, value)
        count = self.repo.has_transactions(cat_id)
        return CategoryOut(**{**vars(cat), "transaction_count": count})

    def delete(self, cat_id: str) -> dict:
        count = self.repo.has_transactions(cat_id)
        if count > 0:
            raise HTTPException(status.HTTP_409_CONFLICT, f"La categoría tiene {count} transacciones.")
        if not self.repo.delete(cat_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Categoría '{cat_id}' no encontrada")
        return {"message": "Categoría eliminada", "id": cat_id}
