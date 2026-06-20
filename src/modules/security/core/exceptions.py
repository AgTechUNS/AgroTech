"""
exceptions.py ÔÇö Excepciones personalizadas y handlers globales de AgTechUNS.

Toda excepci├│n del sistema produce el mismo esquema JSON:

    {
        "error": {
            "code":    "SNAKE_UPPER_CASE",
            "message": "Descripci├│n legible para el cliente.",
            "details": "Informaci├│n adicional opcional."
        }
    }

Uso en main.py
--------------
    from modules.security.core.exceptions import register_exception_handlers
    register_exception_handlers(app)
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# Formato est├índar de respuesta de error
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

def _error_response(code: str, message: str, details: Any = None) -> dict:
    """Construye el cuerpo JSON est├índar de error."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# Clase base
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

class AgTechException(HTTPException):
    """
    Clase base para todas las excepciones de negocio de AgTechUNS.

    Garantiza que cualquier excepci├│n hija produzca el esquema JSON est├índar
    { error: { code, message, details } } al ser capturada por el handler global.

    Par├ímetros
    ----------
    status_code : c├│digo HTTP (400, 401, 403, 404, 429...).
    code        : c├│digo de negocio en SNAKE_UPPER_CASE.
    message     : descripci├│n legible para el cliente.
    details     : informaci├│n adicional opcional (nunca detalles internos).
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


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# Excepciones de identidad ÔÇö auth/
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

class InvalidCredentialsException(AgTechException):
    """Login fallido: email o contrase├▒a incorrectos."""

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="CREDENTIALS_INVALID",
            message="Email o contrase├▒a incorrectos.",
            details=details,
        )


class ResetTokenInvalidException(AgTechException):
    """Token de recuperaci├│n de contrase├▒a inv├ílido o expirado."""

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="RESET_TOKEN_INVALID",
            message="El token de recuperaci├│n es inv├ílido o ya expir├│.",
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


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# Excepciones de interceptor ÔÇö security/
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

class InvalidTokenException(AgTechException):
    """
    Token JWT ausente, malformado o con firma inv├ílida.
    Disparada por get_current_user.py al fallar la verificaci├│n.
    Fuerza un nuevo login en el cliente.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_INVALID",
            message="Token de autenticaci├│n inv├ílido. Inici├í sesi├│n nuevamente.",
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
            message="La sesi├│n expir├│. Actualiz├í tu token o inici├í sesi├│n nuevamente.",
            details=details,
        )


class InsufficientPermissionsException(AgTechException):
    """
    Usuario autenticado pero sin el rol requerido (RBAC).
    Disparada por require_role() en security/roles.py.
    Ej: Agr├│nomo intentando acceder a funciones de Administrador.
    """

    def __init__(self, required_role: str | None = None, details: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="INSUFFICIENT_PERMISSIONS",
            message="No ten├®s permisos para realizar esta acci├│n.",
            details=details or (f"Rol requerido: {required_role}" if required_role else None),
        )


class ResourceOwnershipException(AgTechException):
    """
    Usuario autenticado pero no es due├▒o del recurso solicitado.
    Ej: Agr├│nomo consultando una parcela que no le pertenece.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="RESOURCE_OWNERSHIP_DENIED",
            message="No ten├®s acceso a este recurso.",
            details=details,
        )


class RateLimitExceededException(AgTechException):
    """
    Demasiados intentos en un per├¡odo corto (fuerza bruta).
    Producida por slowapi y normalizada al formato est├índar.
    """

    def __init__(self, details: Any = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message="Demasiados intentos. Esper├í un momento e intent├í de nuevo.",
            details=details,
        )


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# Handlers globales ÔÇö se registran en main.py
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

async def _agtech_exception_handler(request: Request, exc: AgTechException) -> JSONResponse:
    """
    Captura cualquier AgTechException y la serializa al formato est├índar.
    Loguea errores de seguridad (401, 403, 429) para auditor├¡a.
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
    Captura errores de validaci├│n de Pydantic (campos faltantes o malformados)
    y los normaliza al formato est├índar. Oculta detalles t├®cnicos internos.
    """
    # Extraemos solo los campos y mensajes ÔÇö sin stack traces ni paths internos
    fields = [
        {"field": " ÔåÆ ".join(str(loc) for loc in error["loc"]), "issue": error["msg"]}
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_response(
            code="VALIDATION_ERROR",
            message="Los datos enviados son inv├ílidos.",
            details=fields,
        ),
    )


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Captura excepciones de slowapi y las normaliza al formato est├índar.
    Loguea el evento para auditor├¡a de fuerza bruta.
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
            message="Demasiados intentos. Esper├í un momento e intent├í de nuevo.",
            details=str(exc.detail),
        ),
    )


async def _http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:  # noqa: ARG001
    """
    Captura HTTPException desnudas lanzadas por FastAPI o librer├¡as externas.
    Sin este handler caer├¡an al catch-all de Exception y devolver├¡an 500,
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
    Captura cualquier excepci├│n no controlada (500).
    Loguea el error completo internamente pero devuelve un mensaje
    gen├®rico al cliente ÔÇö nunca detalles de PostgreSQL o del stack interno.
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
            message="Ocurri├│ un error interno. Intent├í de nuevo m├ís tarde.",
            details=None,  # nunca exponer detalles t├®cnicos al cliente
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos los handlers en la app FastAPI.
    Llamar en main.py una sola vez, antes de montar los routers.

    Uso:
        from modules.security.core.exceptions import register_exception_handlers
        register_exception_handlers(app)
    """
    app.add_exception_handler(AgTechException, _agtech_exception_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
