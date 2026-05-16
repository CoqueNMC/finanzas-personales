from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.connection import get_db
from backend.schemas import CategoryCreate, CategoryUpdate, CategoryOut
from backend.services import CategoryService
from backend.core.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/categories", tags=["Categorias"])

def get_service(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CategoryService(db, current_user)

@router.get("/", response_model=list[CategoryOut])
def list_categories(svc: CategoryService = Depends(get_service)):
    return svc.get_all()

@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, svc: CategoryService = Depends(get_service)):
    return svc.create(data)

@router.patch("/{cat_id}/", response_model=CategoryOut)
def update_category(cat_id: str, data: CategoryUpdate, svc: CategoryService = Depends(get_service)):
    return svc.update(cat_id, data)

@router.delete("/{cat_id}/")
def delete_category(cat_id: str, svc: CategoryService = Depends(get_service)):
    return svc.delete(cat_id)