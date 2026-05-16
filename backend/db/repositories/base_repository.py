"""
Repositorio base genérico. Define las operaciones CRUD comunes.
Los repositorios específicos heredan de aquí (DRY).
"""
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List
from backend.db.connection import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.db.get(self.model, id)

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, id: str) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.flush()
        return True

    def exists(self, id: str) -> bool:
        return self.db.get(self.model, id) is not None
