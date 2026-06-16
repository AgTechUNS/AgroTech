"""
exceptions.py — Excepciones personalizadas y handlers globales de AgTechUNS.

Toda excepción del sistema produce el mismo esquema JSON:

    {
        "error": {
            "code":    "SNAKE_UPPER_CASE",
            "message": "Descripción legible para el cliente.",
            "details": "Información adicional opcional."
        }
    }

Uso en main.py
--------------
    from core.exceptions import register_exception_handlers
    register_exception_handlers(app)
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Formato estándar de respuesta de error
# ──────────────────────────────────────────────

def _error_response(code: str, message: str, details: Any = None) -> dict:
    """Construye el cuerpo JSON estándar de error."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


# ──────────────────────────────────────────────
# Clase base
# ──────────────────────────────────────────────

class AgTechException(HTTPException):
    """
    Clase base para todas las excepciones de negocio de AgTechUNS.

    Garantiza que cualquier excepción hija produzca el esquema JSON estándar
    { error: { code, message, details } } al ser capturada por el handler global.

    Parámetros
    ----------
    status_code : código HTTP (400, 401, 403, 404, 429...).
    code        : código de negocio en SNAKE_UPPER_CASE.
    message     : descripción legible para el cliente.
    details     : información adicional opcional (nunca detalles internos).
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details


# ──────────────────────────────────────────────
# Excepciones de identidad — auth/
# ──────────────────────────────────────────────

class InvalidCredentialsException(AgTechException):
    """Login fallido: email o contraseña incorrectos."""

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="CREDENTIALS_INVALID",
            message="Email o contraseña incorrectos.",
            details=details,
        )


class ResetTokenInvalidException(AgTechException):
    """Token de recuperación de contraseña inválido o expirado."""

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="RESET_TOKEN_INVALID",
            message="El token de recuperación es inválido o ya expiró.",
            details=details,
        )


class UserNotFoundException(AgTechException):
    """Usuario no encontrado en el repositorio relacional."""

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message="Usuario no encontrado.",
            details=details,
        )


# ──────────────────────────────────────────────
# Excepciones de interceptor — security/
# ──────────────────────────────────────────────

class InvalidTokenException(AgTechException):
    """
    Token JWT ausente, malformado o con firma inválida.
    Disparada por get_current_user.py al fallar la verificación.
    Fuerza un nuevo login en el cliente.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_INVALID",
            message="Token de autenticación inválido. Iniciá sesión nuevamente.",
            details=details,
        )


class TokenExpiredException(AgTechException):
    """
    Token JWT expirado.
    Separado de TOKEN_INVALID para que el frontend pueda intentar
    refresh antes de forzar un nuevo login.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_EXPIRED",
            message="La sesión expiró. Actualizá tu token o iniciá sesión nuevamente.",
            details=details,
        )


class InsufficientPermissionsException(AgTechException):
    """
    Usuario autenticado pero sin el rol requerido (RBAC).
    Disparada por require_role() en security/roles.py.
    Ej: Agrónomo intentando acceder a funciones de Administrador.
    """

    def __init__(self, required_role: str | None = None, details: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="INSUFFICIENT_PERMISSIONS",
            message="No tenés permisos para realizar esta acción.",
            details=details or (f"Rol requerido: {required_role}" if required_role else None),
        )


class ResourceOwnershipException(AgTechException):
    """
    Usuario autenticado pero no es dueño del recurso solicitado.
    Ej: Agrónomo consultando una parcela que no le pertenece.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="RESOURCE_OWNERSHIP_DENIED",
            message="No tenés acceso a este recurso.",
            details=details,
        )


class RateLimitExceededException(AgTechException):
    """
    Demasiados intentos en un período corto (fuerza bruta).
    Producida por slowapi y normalizada al formato estándar.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message="Demasiados intentos. Esperá un momento e intentá de nuevo.",
            details=details,
        )


# ──────────────────────────────────────────────
# Handlers globales — se registran en main.py
# ──────────────────────────────────────────────

async def _agtech_exception_handler(request: Request, exc: AgTechException) -> JSONResponse:
    """
    Captura cualquier AgTechException y la serializa al formato estándar.
    Loguea errores de seguridad (401, 403, 429) para auditoría.
    """
    if exc.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
        status.HTTP_429_TOO_MANY_REQUESTS,
    ):
        logger.warning(
            "Evento de seguridad | code=%s | path=%s | ip=%s",
            exc.code,
            request.url.path,
            request.client.host if request.client else "desconocida",
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_response(exc.code, exc.message, exc.details),
    )


async def _validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Captura errores de validación de Pydantic (campos faltantes o malformados)
    y los normaliza al formato estándar. Oculta detalles técnicos internos.
    """
    # Extraemos solo los campos y mensajes — sin stack traces ni paths internos
    fields = [
        {"field": " → ".join(str(loc) for loc in error["loc"]), "issue": error["msg"]}
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_response(
            code="VALIDATION_ERROR",
            message="Los datos enviados son inválidos.",
            details=fields,
        ),
    )


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Captura excepciones de slowapi y las normaliza al formato estándar.
    Loguea el evento para auditoría de fuerza bruta.
    """
    logger.warning(
        "Rate limit excedido | path=%s | ip=%s | limit=%s",
        request.url.path,
        request.client.host if request.client else "desconocida",
        str(exc.detail),
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=_error_response(
            code="RATE_LIMIT_EXCEEDED",
            message="Demasiados intentos. Esperá un momento e intentá de nuevo.",
            details=str(exc.detail),
        ),
    )


async def _http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:  # noqa: ARG001
    """
    Captura HTTPException desnudas lanzadas por FastAPI o librerías externas.
    Sin este handler caerían al catch-all de Exception y devolverían 500,
    perdiendo el status code original.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
        ),
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Captura cualquier excepción no controlada (500).
    Loguea el error completo internamente pero devuelve un mensaje
    genérico al cliente — nunca detalles de PostgreSQL o del stack interno.
    """
    logger.exception(
        "Error interno no controlado | path=%s | ip=%s",
        request.url.path,
        request.client.host if request.client else "desconocida",
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_response(
            code="INTERNAL_ERROR",
            message="Ocurrió un error interno. Intentá de nuevo más tarde.",
            details=None,  # nunca exponer detalles técnicos al cliente
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos los handlers en la app FastAPI.
    Llamar en main.py una sola vez, antes de montar los routers.

    Uso:
        from core.exceptions import register_exception_handlers
        register_exception_handlers(app)
    """
    app.add_exception_handler(AgTechException, _agtech_exception_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)