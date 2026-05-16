"""
Inserta las categorias por defecto.
Ejecutar: python scripts/seed_categories.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.db.connection import SessionLocal
from backend.models import Category
from backend.services.id_service import generate_id

DEFAULT_CATEGORIES = [
    ("cat_1",  "Alimentacion",        "🍽️", "#22d48f"),
    ("cat_2",  "Transporte",          "🏍️", "#3b9eff"),
    ("cat_3",  "Regalos",             "🎁", "#f472b6"),
    ("cat_4",  "Suscripciones",       "📱", "#7c6aff"),
    ("cat_5",  "Servicios del hogar", "🏠", "#ffad3b"),
    ("cat_6",  "Ropa y accesorios",   "👗", "#c084fc"),
    ("cat_7",  "Salud y seguros",     "🏥", "#ff7b54"),
    ("cat_8",  "Entretenimiento",     "🎬", "#ff5e7a"),
    ("cat_9",  "Inversion",           "📈", "#22d48f"),
    ("cat_10", "Nomina e ingresos",   "💼", "#3b9eff"),
    ("cat_11", "Finanzas e impuestos","🏦", "#888888"),
    ("cat_12", "Gimnasio",            "💪", "#ff7b54"),
    ("cat_13", "Mascotas",            "🐾", "#ffad3b"),
    ("cat_14", "Prestamos",           "🤝", "#ff5e7a"),
    ("cat_15", "Varios",              "📦", "#555555"),
]

def seed():
    db = SessionLocal()
    try:
        inserted = 0
        for cat_id, name, emoji, color in DEFAULT_CATEGORIES:
            if not db.get(Category, cat_id):
                db.add(Category(id=cat_id, name=name, emoji=emoji, color=color))
                inserted += 1
        db.commit()
        print(f"{inserted} categorias insertadas.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
