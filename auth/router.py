"""
auth/router.py — Endpoints públicos del Authentication Controller.

Expone las rutas de identidad de AgTechUNS:
  POST /auth/login           → Sign In Controller
  POST /auth/reset-request   → Reset Password Controller (paso 1)
  POST /auth/reset-confirm   → Reset Password Controller (paso 2)

Principios:
  - Thin Controller: recibe, valida con Pydantic y delega a auth/service.py.
  - Rate limiting: slowapi protege contra fuerza bruta por IP.
  - Status codes: 200 login, 401 credenciales, 429 rate limit.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_db
from core.limiter import limiter
from auth.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RefreshResponse,
    ResetPasswordConfirm,
    ResetPasswordRequest,
    TokenResponse,
)
from auth.service import (
    build_token_response,
    confirm_password_reset,
    refresh_access_token,
    request_password_reset,
    verify_credentials,
)
from core.config import get_settings

logger   = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ──────────────────────────────────────────────
# POST /auth/login
# ──────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    summary="Inicio de sesión",
    description=(
        "Valida las credenciales del usuario y emite un JWT. "
        "Limitado a 5 intentos por minuto por IP para prevenir fuerza bruta."
    ),
    responses={
        200: {"description": "Login exitoso. Retorna access y refresh token."},
        401: {"description": "Credenciales inválidas."},
        422: {"description": "Datos de entrada inválidos."},
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
    Sign In Controller — Modo Activo.

    Flujo:
      1. Pydantic valida LoginRequest (email, password ≥ 8 chars).
      2. service.verify_credentials() busca en PostgreSQL y compara hash bcrypt.
      3. service.build_token_response() emite JWT con contexto del usuario.
    """
    usuario = await verify_credentials(
        email=str(body.email_usuario),
        password=body.password,
        db=db,
    )
    return build_token_response(usuario)


# ──────────────────────────────────────────────
# POST /auth/reset-request
# ──────────────────────────────────────────────

@router.post(
    "/reset-request",
    response_model=MessageResponse,
    status_code=200,
    summary="Solicitud de recuperación de contraseña",
    description=(
        "Genera un token de un solo uso y lo envía al email registrado. "
        "Respuesta siempre igual para no exponer si el email existe."
    ),
    responses={
        200: {"description": "Solicitud procesada."},
        422: {"description": "Email inválido."},
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
    Reset Password Controller — paso 1.

    Responde siempre con el mismo mensaje genérico (anti-enumeración).
    La lógica real (si el email existe o no) es transparente al cliente.
    """
    await request_password_reset(email=str(body.email_usuario), db=db)

    return MessageResponse(
        message="Si el email está registrado en el sistema, recibirás las instrucciones de recuperación."
    )


# ──────────────────────────────────────────────
# POST /auth/reset-confirm
# ──────────────────────────────────────────────

@router.post(
    "/reset-confirm",
    response_model=MessageResponse,
    status_code=200,
    summary="Confirmación de nueva contraseña",
    description="Valida el token de recuperación y actualiza la contraseña del usuario.",
    responses={
        200: {"description": "Contraseña actualizada exitosamente."},
        400: {"description": "Token inválido o expirado."},
        422: {"description": "Datos de entrada inválidos."},
        429: {"description": "Demasiados intentos. Rate limit excedido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_RESET)
async def reset_confirm(
    request: Request,  # noqa: ARG001 — requerido por slowapi para extraer la IP
    body: ResetPasswordConfirm,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Reset Password Controller — paso 2.

    Valida el token de un solo uso, hashea la nueva contraseña
    e invalida el token para que no pueda reutilizarse.
    """
    await confirm_password_reset(payload=body, db=db)

    return MessageResponse(message="Contraseña actualizada exitosamente.")


# ──────────────────────────────────────────────
# POST /auth/refresh
# ──────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=200,
    summary="Renovación del access token",
    description=(
        "Emite un nuevo access token a partir de un refresh token válido. "
        "No requiere autenticación adicional — el refresh token es la credencial."
    ),
    responses={
        200: {"description": "Access token renovado exitosamente."},
        401: {"description": "Refresh token inválido o de tipo incorrecto."},
        422: {"description": "Datos de entrada inválidos."},
        429: {"description": "Demasiados intentos. Rate limit excedido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_REFRESH)
async def refresh(
    request: Request,  # noqa: ARG001 — requerido por slowapi para extraer la IP
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    """
    Rota el access token usando el refresh token.

    No emite un nuevo refresh token — la sesión larga no se extiende.
    El rol y campos asignados se leen desde DB para reflejar cambios recientes.
    """
    return await refresh_access_token(body.refresh_token, db)