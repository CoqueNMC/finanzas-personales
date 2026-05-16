"""
Entry point de FastAPI.
Registra routers y configura middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import get_settings
from backend.db.connection import health_check
from backend.api.routes import (
    accounts_router, categories_router,
    transactions_router, dashboard_router, auth_router,
)

settings = get_settings()

app = FastAPI(
    title="Finanzas Personales API",
    version="1.0.0",
    docs_url="/api/docs" if settings.is_development else None,
    redirect_slashes=False,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas bajo /api/v1
PREFIX = "/api/v1"
app.include_router(accounts_router,     prefix=PREFIX)
app.include_router(categories_router,   prefix=PREFIX)
app.include_router(transactions_router, prefix=PREFIX)
app.include_router(dashboard_router,    prefix=PREFIX)
app.include_router(auth_router,         prefix=PREFIX)

@app.get("/api/health")
def health():
    return {"status": "ok" if health_check() else "db_error", "version": "1.0.0"}

# Servir el frontend en produccion
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
