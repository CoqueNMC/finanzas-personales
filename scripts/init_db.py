"""
Crea todas las tablas en la base de datos configurada.
Ejecutar: python scripts/init_db.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.db.connection import engine, Base
from backend.models import Account, Category, Transaction  # Registra los modelos

def init():
    print(f"Creando tablas en: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

if __name__ == "__main__":
    init()
