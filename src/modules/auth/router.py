"""
auth/router.py ÔÇö Endpoints p├║blicos del Authentication Controller.

Expone las rutas de identidad de AgTechUNS:
  POST /auth/login           ÔåÆ Sign In Controller
  POST /auth/reset-request   ÔåÆ Reset Password Controller (paso 1)
  POST /auth/reset-confirm   ÔåÆ Reset Password Controller (paso 2)

Principios:
  - Thin Controller: recibe, valida con Pydantic y delega a auth/service.py.
  - Rate limiting: slowapi protege contra fuerza bruta por IP.
  - Status codes: 200 login, 401 credenciales, 429 rate limit.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.dependencies import get_db
from modules.security.core.limiter import limiter
from modules.auth.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RefreshResponse,
    ResetPasswordConfirm,
    ResetPasswordRequest,
    TokenResponse,
)
from modules.auth.service import (
    build_token_response,
    confirm_password_reset,
    refresh_access_token,
    request_password_reset,
    verify_credentials,
)
from modules.security.core.config import get_settings

logger   = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# POST /auth/login
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    summary="Inicio de sesi├│n",
    description=(
        "Valida las credenciales del usuario y emite un JWT. "
        "Limitado a 5 intentos por minuto por IP para prevenir fuerza bruta."
    ),
    responses={
        200: {"description": "Login exitoso. Retorna access y refresh token."},
        401: {"description": "Credenciales inv├ílidas."},
        422: {"description": "Datos de entrada inv├ílidos."},
        429: {"description": "Demasiados intentos. Rate limit excedido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,  # requerido por slowapi para extraer la IP
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Sign In Controller ÔÇö Modo Activo.

    Flujo:
      1. Pydantic valida LoginRequest (email, password ÔëÑ 8 chars).
      2. service.verify_credentials() busca en PostgreSQL y compara hash bcrypt.
      3. service.build_token_response() emite JWT con contexto del usuario.
    """
    usuario = await verify_credentials(
        email=str(body.email_usuario),
        password=body.password,
        db=db,
    )
    return build_token_response(usuario)


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# POST /auth/reset-request
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

@router.post(
    "/reset-request",
    response_model=MessageResponse,
    status_code=200,
    summary="Solicitud de recuperaci├│n de contrase├▒a",
    description=(
        "Genera un token de un solo uso y lo env├¡a al email registrado. "
        "Respuesta siempre igual para no exponer si el email existe."
    ),
    responses={
        200: {"description": "Solicitud procesada."},
        422: {"description": "Email inv├ílido."},
        429: {"description": "Demasiados intentos. Rate limit excedido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_RESET)
async def reset_request(
    request: Request,
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Reset Password Controller ÔÇö paso 1.

    Responde siempre con el mismo mensaje gen├®rico (anti-enumeraci├│n).
    La l├│gica real (si el email existe o no) es transparente al cliente.
    """
    await request_password_reset(email=str(body.email_usuario), db=db)

    return MessageResponse(
        message="Si el email est├í registrado en el sistema, recibir├ís las instrucciones de recuperaci├│n."
    )


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# POST /auth/reset-confirm
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

@router.post(
    "/reset-confirm",
    response_model=MessageResponse,
    status_code=200,
    summary="Confirmaci├│n de nueva contrase├▒a",
    description="Valida el token de recuperaci├│n y actualiza la contrase├▒a del usuario.",
    responses={
        200: {"description": "Contrase├▒a actualizada exitosamente."},
        400: {"description": "Token inv├ílido o expirado."},
        422: {"description": "Datos de entrada inv├ílidos."},
        429: {"description": "Demasiados intentos. Rate limit excedido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_RESET)
async def reset_confirm(
    request: Request,  # noqa: ARG001 ÔÇö requerido por slowapi para extraer la IP
    body: ResetPasswordConfirm,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Reset Password Controller ÔÇö paso 2.

    Valida el token de un solo uso, hashea la nueva contrase├▒a
    e invalida el token para que no pueda reutilizarse.
    """
    await confirm_password_reset(payload=body, db=db)

    return MessageResponse(message="Contrase├▒a actualizada exitosamente.")


# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
# POST /auth/refresh
# ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=200,
    summary="Renovaci├│n del access token",
    description=(
        "Emite un nuevo access token a partir de un refresh token v├ílido. "
        "No requiere autenticaci├│n adicional ÔÇö el refresh token es la credencial."
    ),
    responses={
        200: {"description": "Access token renovado exitosamente."},
        401: {"description": "Refresh token inv├ílido o de tipo incorrecto."},
        422: {"description": "Datos de entrada inv├ílidos."},
        429: {"description": "Demasiados intentos. Rate limit excedido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_REFRESH)
async def refresh(
    request: Request,  # noqa: ARG001 ÔÇö requerido por slowapi para extraer la IP
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    """
    Rota el access token usando el refresh token.

    No emite un nuevo refresh token ÔÇö la sesi├│n larga no se extiende.
    El rol y campos asignados se leen desde DB para reflejar cambios recientes.
    """
    return await refresh_access_token(body.refresh_token, db)
