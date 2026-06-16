"""
token_service.py — Lógica criptográfica de tokens JWT.

Responsabilidades:
  - create_access_token()  : firma y emite el token de sesión corta.
  - create_refresh_token() : firma y emite el token de renovación.
  - decode_token()         : verifica firma, expiración y retorna el payload.

Principios de diseño:
  - Stateless: ninguna función consulta la base de datos.
    Toda la información de autorización viaja dentro del JWT.
  - Clave secreta: obtenida desde core/config.get_secret_key()
    que resuelve Vault (prod) o .env (dev). Nunca hardcodeada.
  - Algoritmos soportados: HS256 (simétrico) y RS256 (asimétrico),
    según ALGORITHM configurado en core/config.

Consumidores:
  - auth/service.py            → create_access_token(), create_refresh_token()
  - security/get_current_user  → decode_token()
"""

import logging
from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

from core.config import get_secret_key, get_settings
from core.enums import RoleEnum
from core.exceptions import InvalidTokenException, TokenExpiredException
from security.schemas import UserContext

logger = logging.getLogger(__name__)

# Claim interno que identifica el tipo de token en el payload
_TOKEN_TYPE_CLAIM = "token_type"


# ──────────────────────────────────────────────
# Helpers privados
# ──────────────────────────────────────────────

def _get_sign_key() -> str:
    """Clave para firmar tokens. RS256 → private key. HS256 → secret."""
    settings = get_settings()
    if settings.ALGORITHM == "RS256":
        return settings.PRIVATE_KEY.get_secret_value()
    return get_secret_key()


def _get_verify_key() -> str:
    """Clave para verificar tokens. RS256 → public key. HS256 → secret."""
    settings = get_settings()
    if settings.ALGORITHM == "RS256":
        return settings.PUBLIC_KEY.get_secret_value()
    return get_secret_key()


def _build_payload(
    user_context: UserContext,
    token_type: str,
    expire: datetime,
) -> dict:
    """
    Construye el payload JWT con el contexto del usuario.

    Campos estándar JWT:
      sub  : subject — email_usuario (PK natural del sistema)
      exp  : expiration — validado automáticamente por python-jose
      iat  : issued at — momento de emisión

    Campos de negocio AgTechUNS:
      role            : rol del usuario (RoleEnum)
      assigned_fields : campos/parcelas asignadas
      token_type      : "access" o "refresh"
    """
    return {
        "sub": user_context.user_id,
        "role": user_context.role.value,
        "assigned_fields": user_context.assigned_fields,
        _TOKEN_TYPE_CLAIM: token_type,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }


# ──────────────────────────────────────────────
# API pública
# ──────────────────────────────────────────────

def create_access_token(user_context: UserContext) -> tuple[str, int]:
    """
    Emite un token JWT de acceso (sesión corta).

    Llamado por auth/service.py tras verificar credenciales exitosamente.

    Parámetros
    ----------
    user_context : contexto del usuario autenticado (email, rol, campos).

    Retorna
    -------
    Tupla (token_jwt, expires_in_seconds) para poblar el TokenResponse.
    """
    settings      = get_settings()
    sign_key      = _get_sign_key()

    expires_delta   = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire          = datetime.now(timezone.utc) + expires_delta
    expires_in      = int(expires_delta.total_seconds())

    payload = _build_payload(user_context, token_type="access", expire=expire)
    token   = jwt.encode(payload, sign_key, algorithm=settings.ALGORITHM)

    logger.info(
        "Access token emitido | user=%s | role=%s | exp=%s",
        user_context.user_id,
        user_context.role.value,
        expire.isoformat(),
    )

    return token, expires_in


def create_refresh_token(user_context: UserContext) -> str:
    """
    Emite un token JWT de renovación (sesión larga).

    Payload mínimo — solo sub y expiración.
    No incluye rol ni campos para minimizar exposición en caso de robo.

    Llamado por auth/service.py junto con create_access_token().

    Parámetros
    ----------
    user_context : contexto del usuario autenticado.

    Retorna
    -------
    Token JWT de refresh como string.
    """
    settings = get_settings()
    sign_key = _get_sign_key()

    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub":             user_context.user_id,
        _TOKEN_TYPE_CLAIM: "refresh",
        "exp":             expire,
        "iat":             datetime.now(timezone.utc),
    }

    return jwt.encode(payload, sign_key, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> UserContext:
    """
    Decodifica y valida un JWT. Retorna el UserContext si es válido.

    Llamado por security/get_current_user.py en cada request protegido.
    No consulta la base de datos — validación 100% stateless.

    Parámetros
    ----------
    token         : JWT recibido en el header Authorization: Bearer.
    expected_type : "access" o "refresh". Valida el claim token_type.

    Retorna
    -------
    UserContext con los datos del usuario extraídos del payload.

    Lanza
    -----
    TokenExpiredException  : si el token venció (exp < now).
    InvalidTokenException  : si la firma es inválida, el token está
                             malformado o el tipo no coincide.
    """
    settings   = get_settings()
    verify_key = _get_verify_key()

    try:
        payload = jwt.decode(
            token,
            verify_key,
            algorithms=[settings.ALGORITHM],
        )

    except ExpiredSignatureError:
        logger.warning("Token expirado recibido.")
        raise TokenExpiredException()

    except JWTError as exc:
        logger.warning("Token inválido recibido: %s", str(exc))
        raise InvalidTokenException()

    # Validar tipo de token
    if payload.get(_TOKEN_TYPE_CLAIM) != expected_type:
        logger.warning(
            "Tipo de token incorrecto | esperado=%s | recibido=%s",
            expected_type,
            payload.get(_TOKEN_TYPE_CLAIM),
        )
        raise InvalidTokenException(
            details=f"Se esperaba un token de tipo '{expected_type}'."
        )

    # Extraer campos del payload
    user_id         = payload.get("sub")
    role            = payload.get("role")
    assigned_fields = payload.get("assigned_fields", [])

    if not user_id:
        logger.warning("Payload JWT incompleto: falta sub.")
        raise InvalidTokenException(details="Payload del token incompleto.")

    # Para refresh tokens el rol no viaja en el payload — el caller enriquece
    # el contexto desde DB. Se retorna un UserContext parcial con placeholder.
    if expected_type == "refresh":
        return UserContext(
            user_id=user_id,
            role=RoleEnum.AGRONOMO,
            assigned_fields=[],
        )

    if not role:
        logger.warning("Payload JWT incompleto: falta role.")
        raise InvalidTokenException(details="Payload del token incompleto.")

    try:
        return UserContext(
            user_id=user_id,
            role=role,
            assigned_fields=assigned_fields,
        )
    except Exception:
        logger.warning("No se pudo construir UserContext desde el payload.")
        raise InvalidTokenException(details="Payload del token malformado.")