from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.models import User, PasswordResetToken
from backend.schemas.auth import UserRegister, UserLogin, TokenOut, UserOut
from backend.core.config import get_settings
from backend.services.id_service import generate_id
import secrets

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.app_secret_key
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: UserRegister) -> TokenOut:
        if not settings.allow_register:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "El registro está desactivado")
        existing = self.db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "El email ya está registrado")
        user = User(
            id=generate_id("usr"),
            email=data.email,
            name=data.name,
            password_hash=pwd_context.hash(data.password),
        )
        self.db.add(user)
        self.db.flush()
        self._seed_default_categories(user.id)
        return self._build_token(user)

    def login(self, data: UserLogin) -> TokenOut:
        user = self.db.query(User).filter(User.email == data.email).first()
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales incorrectas")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")
        return self._build_token(user)

    def change_password(self, user: User, current_password: str, new_password: str) -> dict:
        if not pwd_context.verify(current_password, user.password_hash):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Contraseña actual incorrecta")
        user.password_hash = pwd_context.hash(new_password)
        self.db.flush()
        return {"message": "Contraseña actualizada correctamente"}

    def request_password_reset(self, email: str) -> str:
        user = self.db.query(User).filter(User.email == email).first()
        # Siempre responde igual para no revelar si el email existe
        if not user or not user.is_active:
            return "ok"
        # Invalidar tokens anteriores
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        ).update({"used": True})
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            id=generate_id("rst"),
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        self.db.add(reset_token)
        self.db.flush()
        return token

    def reset_password(self, token: str, new_password: str) -> dict:
        reset = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
        ).first()
        if not reset:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido")
        if reset.expires_at < datetime.utcnow():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token expirado")
        user = self.db.query(User).filter(User.id == reset.user_id).first()
        user.password_hash = pwd_context.hash(new_password)
        reset.used = True
        self.db.flush()
        return {"message": "Contraseña restablecida correctamente"}

    def _build_token(self, user: User) -> TokenOut:
        expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
        payload = {"sub": user.id, "email": user.email, "exp": expire}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return TokenOut(
            access_token=token,
            user=UserOut.model_validate(user),
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado")
    
    def _seed_default_categories(self, user_id: str):
        from backend.models import Category
        defaults = [
            ("Alimentación",        "🍽️", "#22d48f"),
            ("Transporte",          "🏍️", "#3b9eff"),
            ("Regalos",             "🎁", "#f472b6"),
            ("Suscripciones",       "📱", "#7c6aff"),
            ("Servicios del hogar", "🏠", "#ffad3b"),
            ("Ropa y accesorios",   "👗", "#c084fc"),
            ("Salud y seguros",     "🏥", "#ff7b54"),
            ("Entretenimiento",     "🎬", "#ff5e7a"),
            ("Inversión",           "📈", "#22d48f"),
            ("Nómina e ingresos",   "💼", "#3b9eff"),
            ("Finanzas e impuestos","🏦", "#888888"),
            ("Gimnasio",            "💪", "#ff7b54"),
            ("Mascotas",            "🐾", "#ffad3b"),
            ("Préstamos",           "🤝", "#ff5e7a"),
            ("Créditos e hipoteca", "🏡", "#3b9eff"),
            ("Varios",              "📦", "#555555"),
        ]
        for name, emoji, color in defaults:
            cat = Category(
                id=generate_id("cat"),
                name=name,
                emoji=emoji,
                color=color,
                user_id=user_id,
            )
            self.db.add(cat)
        self.db.flush()