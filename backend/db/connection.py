"""
─────────────────────────────────────────────────────────────────────
  CONEXIÓN A BASE DE DATOS
  
  Este es el ÚNICO archivo que debes modificar para cambiar de motor
  de base de datos. El resto de la aplicación es 100% agnóstico.

  Motores soportados (cambia DATABASE_URL en .env):
  ┌─────────────────┬────────────────────────────────────────────────────────────────┐
  │ SQL Server      │ mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server │
  │ PostgreSQL      │ postgresql+asyncpg://user:pass@host:5432/db                    │
  │ Supabase        │ postgresql+asyncpg://user:pass@db.xxx.supabase.co:5432/postgres │
  │ SQLite          │ sqlite+aiosqlite:///./finanzas.db                              │
  │ MySQL           │ mysql+aiomysql://user:pass@host:3306/db                        │
  └─────────────────┴────────────────────────────────────────────────────────────────┘
─────────────────────────────────────────────────────────────────────
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from backend.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_engine():
    """
    Construye el engine de SQLAlchemy adaptando los parámetros
    según el motor de BD detectado en DATABASE_URL.
    """
    url = settings.database_url
    kwargs = {}

    # ── SQLite: configuración especial para modo desarrollo ──
    if url.startswith("sqlite"):
        kwargs.update({
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        })

    # ── Motores con pool de conexiones (SQL Server, PostgreSQL, MySQL) ──
    else:
        kwargs.update({
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": settings.db_pool_timeout,
            "pool_pre_ping": True,   # Verifica conexión antes de usarla
            "pool_recycle": 3600,    # Recicla conexiones cada hora
        })

    engine = create_engine(url, echo=settings.is_development, **kwargs)

    logger.info(f"Engine creado: {url.split('@')[-1] if '@' in url else url}")
    return engine


# ── Instancias globales ──────────────────────────────────────────
engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Evita lazy-loading después de commit
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""
    pass


# ── Dependency para FastAPI ──────────────────────────────────────
def get_db():
    """
    Generador de sesión de BD para inyección de dependencias en FastAPI.
    
    Uso en rutas:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def health_check() -> bool:
    """Verifica que la conexión a la BD esté activa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Health check fallido: {e}")
        return False
