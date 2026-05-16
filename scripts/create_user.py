"""
Crea un usuario directamente en la BD sin necesitar registro abierto.
Ejecutar: python scripts/create_user.py --email tu@email.com --name "Tu Nombre" --password "tuPassword123"
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.db.connection import SessionLocal
from backend.models import User
from backend.services.id_service import generate_id
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email: str, name: str, password: str, admin: bool = False):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ Ya existe un usuario con el email {email}")
            return
        user = User(
            id=generate_id("usr"),
            email=email,
            name=name,
            password_hash=pwd_context.hash(password),
            is_active=True,
            is_admin=admin,
        )
        db.add(user)
        db.flush()
        _seed_categories(db, user.id)
        db.commit()
        print(f"✓ Usuario creado exitosamente")
        print(f"  ID:    {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Nombre: {user.name}")
        print(f"  Admin: {user.is_admin}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


def _seed_categories(db, user_id: str):
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
        db.add(cat)
    db.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear usuario en Finanzas Personales")
    parser.add_argument("--email",    required=True, help="Email del usuario")
    parser.add_argument("--name",     required=True, help="Nombre del usuario")
    parser.add_argument("--password", required=True, help="Contraseña (mín. 6 caracteres)")
    parser.add_argument("--admin",    action="store_true", help="Crear como administrador")
    args = parser.parse_args()

    if len(args.password) < 6:
        print("❌ La contraseña debe tener al menos 6 caracteres")
        sys.exit(1)

    create_user(args.email, args.name, args.password, args.admin)