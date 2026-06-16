"""
config.py — Gestión centralizada de configuración y secretos.

Estrategia de obtención de secretos (por entorno):
  - Producción : HashiCorp Vault (hvac). La SECRET_KEY NUNCA vive en disco.
  - Desarrollo  : variables de entorno / archivo .env (fallback explícito).

Métodos de autenticación con Vault:
  - Token   : VAULT_TOKEN (dev / CI)
  - AppRole  : VAULT_ROLE_ID + VAULT_SECRET_ID (producción, Kubernetes/Nomad)
"""

import logging
from functools import lru_cache

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Integración con HashiCorp Vault
# ──────────────────────────────────────────────

def _build_vault_client(vault_addr: str, vault_token: str, role_id: str, secret_id: str):
    """
    Construye y autentica un cliente hvac según el método disponible.

    Prioridad:
      1. AppRole (VAULT_ROLE_ID + VAULT_SECRET_ID) — producción
      2. Token   (VAULT_TOKEN)                      — dev / CI

    Lanza RuntimeError si ningún método está configurado o la autenticación falla.
    """
    try:
        import hvac
    except ImportError:
        raise ImportError(
            "hvac no está instalado. "
            "Instalalo con: pip install hvac"
        )

    client = hvac.Client(url=vault_addr)

    if role_id and secret_id:
        resp = client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id,
        )
        client.token = resp["auth"]["client_token"]
        logger.info("Vault: autenticado con AppRole ✓")

    elif vault_token:
        client.token = vault_token
        logger.warning(
            "Vault: autenticado con token estático. "
            "Usar AppRole en producción."
        )

    else:
        raise RuntimeError(
            "Vault configurado pero sin credenciales. "
            "Definí VAULT_ROLE_ID + VAULT_SECRET_ID (prod) "
            "o VAULT_TOKEN (dev)."
        )

    if not client.is_authenticated():
        raise RuntimeError(
            "No se pudo autenticar con HashiCorp Vault. "
            "Verificá las credenciales y permisos."
        )

    return client


def _fetch_secret_from_vault(
    vault_addr: str,
    vault_token: str,
    role_id: str,
    secret_id: str,
    secret_path: str,
    mount_point: str,
) -> str | None:
    """
    Obtiene la SECRET_KEY desde HashiCorp Vault (KV v2).

    Retorna el valor como string, o None si hvac no está instalado
    (caso desarrollo sin Vault).
    """
    try:
        client = _build_vault_client(vault_addr, vault_token, role_id, secret_id)
        response = client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point=mount_point,
        )
        secret_key = response["data"]["data"].get("SECRET_KEY")

        if not secret_key:
            raise ValueError(
                f"SECRET_KEY no encontrada en Vault path: {mount_point}/{secret_path}"
            )

        logger.info("SECRET_KEY obtenida desde HashiCorp Vault ✓")
        return secret_key

    except ImportError:
        logger.warning(
            "hvac no está instalado. Vault deshabilitado. "
            "Usá solo en desarrollo local."
        )
        return None


def _resolve_secret_key(
    environment: str,
    vault_addr: str,
    vault_token: str,
    role_id: str,
    secret_id: str,
    secret_path: str,
    mount_point: str,
    fallback_key: str,
) -> str:
    """
    Resuelve la SECRET_KEY según el entorno activo:

      ENVIRONMENT=production  → Vault obligatorio. Falla si no está disponible.
      ENVIRONMENT=development → Vault opcional. Fallback a variable de entorno.
    """
    vault_disponible = bool(vault_addr and (vault_token or (role_id and secret_id)))

    if vault_disponible:
        secret = _fetch_secret_from_vault(
            vault_addr, vault_token, role_id, secret_id, secret_path, mount_point
        )
        if secret:
            return secret

    if environment == "production":
        raise RuntimeError(
            "PRODUCCIÓN: SECRET_KEY no pudo obtenerse desde Vault. "
            "Configurá VAULT_ADDR y credenciales AppRole correctamente."
        )

    if not fallback_key:
        raise RuntimeError(
            "SECRET_KEY no configurada. "
            "En desarrollo: definila en .env. "
            "En producción: configurá HashiCorp Vault con AppRole."
        )

    logger.warning(
        "SECRET_KEY leída desde variable de entorno. "
        "Esto es aceptable solo en desarrollo local."
    )
    return fallback_key


# ──────────────────────────────────────────────
# Settings
# ──────────────────────────────────────────────

class Settings(BaseSettings):
    # Entorno
    ENVIRONMENT: str = "development"

    # JWT
    # HS256: clave simétrica. Válido para servicios internos.
    # RS256: clave asimétrica. Recomendado en producción multi-servicio.
    #        Requiere PRIVATE_KEY y PUBLIC_KEY (ver validación abajo).
    ALGORITHM: str = "HS256"

    # RS256 — claves PEM como SecretStr para que no aparezcan en logs ni model_dump()
    PRIVATE_KEY: SecretStr = SecretStr("")  # firma de tokens   (mantener secreto)
    PUBLIC_KEY: SecretStr = SecretStr("")   # verificación       (puede distribuirse)

    # TTLs de tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # Base de datos — SecretStr oculta la URL en logs y model_dump()
    DATABASE_URL: SecretStr = SecretStr("")

    # HashiCorp Vault
    VAULT_ADDR: str = ""
    VAULT_TOKEN: SecretStr = SecretStr("")      # dev / CI
    VAULT_ROLE_ID: str = ""                     # prod (AppRole) — no es secreto
    VAULT_SECRET_ID: SecretStr = SecretStr("")  # prod (AppRole)
    VAULT_SECRET_PATH: str = "agtech/auth"
    VAULT_MOUNT_POINT: str = "secret"           # motor KV montado en Vault

    # SECRET_KEY — solo desarrollo (en prod viene de Vault, esta campo queda vacío)
    SECRET_KEY: SecretStr = SecretStr("")

    # Rate limiting (consumido por slowapi + exceptions.py)
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_RESET: str = "3/minute"
    RATE_LIMIT_REFRESH: str = "30/minute"

    # Notification service
    NOTIFICATION_SERVICE_URL: str = ""

    @model_validator(mode="after")
    def validate_algorithm_keys(self) -> "Settings":
        """
        Valida en startup que RS256 tiene las claves PEM configuradas.
        Falla inmediatamente — no en tiempo de request.
        """
        if self.ALGORITHM == "RS256":
            if (
                not self.PRIVATE_KEY.get_secret_value()
                or not self.PUBLIC_KEY.get_secret_value()
            ):
                raise ValueError(
                    "ALGORITHM=RS256 requiere PRIVATE_KEY y PUBLIC_KEY configuradas. "
                    "Generá un par RSA con:\n"
                    "  openssl genrsa -out private.pem 2048\n"
                    "  openssl rsa -in private.pem -pubout -out public.pem"
                )
        return self

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retorna la instancia única de Settings (singleton por proceso).
    Usar siempre esta función en lugar de instanciar Settings directamente.

    Uso:
        from core.config import get_settings
        settings = get_settings()
    """
    return Settings()


@lru_cache(maxsize=1)
def get_secret_key() -> str:
    """
    Retorna la SECRET_KEY resuelta (Vault o .env según entorno).
    Cacheada para no llamar a Vault en cada request.

    Uso:
        from core.config import get_secret_key
        key = get_secret_key()
    """
    s = get_settings()
    return _resolve_secret_key(
        environment=s.ENVIRONMENT,
        vault_addr=s.VAULT_ADDR,
        vault_token=s.VAULT_TOKEN.get_secret_value(),
        role_id=s.VAULT_ROLE_ID,
        secret_id=s.VAULT_SECRET_ID.get_secret_value(),
        secret_path=s.VAULT_SECRET_PATH,
        mount_point=s.VAULT_MOUNT_POINT,
        fallback_key=s.SECRET_KEY.get_secret_value(),
    )
