import logging
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"

    # JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # Base de datos
    DATABASE_URL: SecretStr = SecretStr("")

    # Clave de firma JWT (solo desarrollo ÔÇö en prod usar variable de entorno segura)
    SECRET_KEY: SecretStr = SecretStr("")

    # Rate limiting
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_RESET: str = "3/minute"
    RATE_LIMIT_REFRESH: str = "30/minute"

    # Notification Component
    NOTIFICATION_SERVICE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_secret_key() -> str:
    key = get_settings().SECRET_KEY.get_secret_value()
    if not key:
        raise RuntimeError("SECRET_KEY no configurada. Definila en .env.")
    return key
