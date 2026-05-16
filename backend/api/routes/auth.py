from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from backend.db.connection import get_db
from backend.schemas.auth import (
    UserRegister, UserLogin, TokenOut,
    ChangePasswordRequest, ResetPasswordRequest, ConfirmResetRequest,
)
from backend.services.auth_service import AuthService
from backend.services.email_service import send_reset_email
from backend.core.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def get_service(db: Session = Depends(get_db)):
    return AuthService(db)


@router.post("/register/", response_model=TokenOut, status_code=201)
def register(data: UserRegister, svc: AuthService = Depends(get_service)):
    return svc.register(data)


@router.post("/login/", response_model=TokenOut)
def login(data: UserLogin, svc: AuthService = Depends(get_service)):
    return svc.login(data)


@router.post("/change-password/")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    svc: AuthService = Depends(get_service),
):
    return svc.change_password(current_user, data.current_password, data.new_password)


@router.post("/forgot-password/")
async def forgot_password(
    data: ResetPasswordRequest,
    request: Request,
    svc: AuthService = Depends(get_service),
):
    token = svc.request_password_reset(data.email)
    if token != "ok":
        base_url = str(request.base_url).rstrip("/")
        # En producción usar la URL del frontend
        frontend_url = "http://localhost:3000"
        user = svc.db.query(__import__('backend.models', fromlist=['User']).User).filter_by(email=data.email).first()
        await send_reset_email(data.email, user.name, token, frontend_url)
    return {"message": "Si el email existe recibirás un correo con instrucciones"}


@router.post("/reset-password/")
def reset_password(data: ConfirmResetRequest, svc: AuthService = Depends(get_service)):
    return svc.reset_password(data.token, data.new_password)