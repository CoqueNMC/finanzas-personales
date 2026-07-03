"""
Configuración central de la aplicación.
Todas las variables de entorno se leen aquí y solo aquí (DRY).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # Base de datos
    database_url: str

    # Servidor
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_env: str = "development"
    app_secret_key: str = "dev-secret-key"
    resend_api_key: str = ""
    allow_register: bool = False
    # CORS
    cors_origins: str = "http://localhost:3000"

    # Pool de conexiones
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    mail_from: str = "finanzas_app@gmail.com"
    mail_username: str = ""
    mail_password: str = ""
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """Instancia única de configuración (singleton via lru_cache)."""
    return Settings()
