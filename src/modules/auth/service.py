"""
auth/service.py — Lógica de negocio del Authentication Controller.

Responsabilidades:
  - verify_credentials()   : valida email/password contra PostgreSQL.
  - build_token_response() : construye el TokenResponse tras login exitoso.
  - request_password_reset(): genera y persiste el token de recuperación.
  - confirm_password_reset(): valida el token y actualiza la contraseña.

Principios:
  - Thin Router: el router solo valida schemas y delega acá.
  - Independencia: sin lógica agrícola — solo identidad y acceso.
  - Stub de Notification: interfaz preparada para cuando el equipo
    defina el contrato del Notification Component.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.models import Usuario, UsuarioRolCampo
from modules.auth.schemas import RefreshResponse, ResetPasswordConfirm, TokenResponse
from modules.security.core.config import get_settings
from modules.security.core.exceptions import (
    InvalidCredentialsException,
    ResetTokenInvalidException,
    UserNotFoundException,
)
from modules.security.core.hashing import hash_password, needs_rehash, verify_password
from modules.security.schemas import UserContext
from modules.security.token_service import create_access_token, create_refresh_token, decode_token

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Helpers privados
# ──────────────────────────────────────────────

async def _get_usuario_by_email(email: str, db: AsyncSession) -> Usuario:
    """
    Busca un usuario activo por email en PostgreSQL.
    Lanza UserNotFoundException si no existe o está inactivo.
    """
    result = await db.execute(
        select(Usuario).where(
            Usuario.email_usuario == email,
            Usuario.is_active.is_(True),
        )
    )
    usuario = result.scalar_one_or_none()

    if usuario is None:
        raise UserNotFoundException()

    return usuario


def _build_user_context(usuario: Usuario) -> UserContext:
    """
    Construye el UserContext a partir del ORM.
    Extrae rol y campos asignados desde la tabla de asociación.
    """
    if not usuario.roles_campos:
        logger.error("Usuario sin roles asignados | email=%s", usuario.email_usuario)
        raise InvalidCredentialsException()

    # Tomar el primer rol — el modelo actual asigna un rol por usuario.
    # Si en el futuro un usuario tiene múltiples roles, este método debe revisarse.
    rol = usuario.roles_campos[0].rol.value
    campos = [str(rc.campo_id) for rc in usuario.roles_campos]

    return UserContext(
        user_id=usuario.email_usuario,
        role=rol,
        assigned_fields=campos,
    )


async def _notify_reset_token(email: str, token: str) -> None:
    """
    Stub del Notification Component.

    El Notification Component vive en el mismo proyecto Python como módulo
    interno (no es un microservicio externo), por lo que la integración final
    será un import directo, no una llamada HTTP:

        from modules.notification.service import send_notification
        await send_notification(
            type="password_reset",
            recipient=email,
            payload={"token": token},
        )

    Pendiente: coordinar con el compañero responsable del Notification Component
    el path exacto del módulo y la firma de su función pública antes de reemplazar
    este stub. Una vez definido, eliminar NOTIFICATION_SERVICE_URL de config.py.
    """
    settings = get_settings()

    if settings.NOTIFICATION_SERVICE_URL:
        # TODO: implementar cuando el equipo defina el contrato
        logger.info(
            "STUB Notification | Llamar a %s con token para %s",
            settings.NOTIFICATION_SERVICE_URL,
            email,
        )
    else:
        # Solo en desarrollo — nunca en producción
        logger.warning(
            "DESARROLLO — Reset token para %s: %s "
            "(configurar NOTIFICATION_SERVICE_URL en producción)",
            email,
            token,
        )


# ──────────────────────────────────────────────
# API pública del service
# ──────────────────────────────────────────────

async def verify_credentials(email: str, password: str, db: AsyncSession) -> Usuario:
    """
    Verifica las credenciales del usuario contra PostgreSQL.

    Flujo:
      1. Busca el usuario activo por email.
      2. Compara la contraseña con el hash almacenado (bcrypt).
      3. Si las credenciales son válidas y el hash es antiguo, lo rehashea.

    Parámetros
    ----------
    email    : email_usuario enviado por la SPA.
    password : contraseña en texto plano enviada por la SPA.
    db       : sesión AsyncSession inyectada por auth/dependencies.py.

    Retorna
    -------
    El objeto Usuario ORM si las credenciales son válidas.

    Lanza
    -----
    InvalidCredentialsException (401) si el email no existe o la contraseña
    no coincide. Mismo error en ambos casos para no exponer cuál falló.
    """
    # Buscamos por email — UserNotFoundException interna se convierte en
    # InvalidCredentialsException para no exponer si el email existe.
    try:
        usuario = await _get_usuario_by_email(email, db)
    except UserNotFoundException:
        raise InvalidCredentialsException()

    if not verify_password(password, usuario.hash_password):
        logger.warning("Credenciales inválidas | email=%s", email)
        raise InvalidCredentialsException()

    # Migración progresiva de rounds bcrypt sin interrumpir al usuario
    if needs_rehash(usuario.hash_password):
        usuario.hash_password = hash_password(password)
        await db.commit()
        logger.info("Hash bcrypt actualizado | email=%s", email)

    return usuario


def build_token_response(usuario: Usuario) -> TokenResponse:
    """
    Construye el TokenResponse tras un login exitoso.

    Coordina con security/token_service para emitir access y refresh token
    con el contexto completo del usuario (email, rol, campos asignados).

    Parámetros
    ----------
    usuario : objeto Usuario ORM validado por verify_credentials().

    Retorna
    -------
    TokenResponse listo para devolver al cliente.
    """
    user_context  = _build_user_context(usuario)
    access_token, expires_in = create_access_token(user_context)
    refresh_token = create_refresh_token(user_context)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> RefreshResponse:
    """
    Renueva el access token consultando el estado actual del usuario en DB.

    Flujo (Opción B — DB refresh):
      1. decode_token() valida firma y expiración — lanza si el token es inválido.
         El UserContext retornado es parcial (solo user_id; rol es placeholder).
      2. _get_usuario_by_email() verifica que el usuario siga activo en DB.
      3. _build_user_context() construye el UserContext fresco con rol y campos
         actuales — refleja cambios de permisos sin necesidad de nuevo login.
      4. create_access_token() emite el nuevo JWT.

    No emite un nuevo refresh token — la sesión larga no se extiende.

    Parámetros
    ----------
    refresh_token : JWT de renovación emitido en el login.
    db            : sesión AsyncSession inyectada por el router.

    Retorna
    -------
    RefreshResponse con el nuevo access_token y expires_in.

    Lanza
    -----
    TokenExpiredException      : si el refresh token venció.
    InvalidTokenException      : si la firma es inválida o el tipo no es "refresh".
    InvalidCredentialsException: si el usuario fue desactivado tras emitir el token.
    """
    partial_context = decode_token(refresh_token, expected_type="refresh")

    usuario = await _get_usuario_by_email(partial_context.user_id, db)
    user_context = _build_user_context(usuario)

    access_token, expires_in = create_access_token(user_context)

    logger.info("Access token renovado | user=%s | role=%s", user_context.user_id, user_context.role.value)

    return RefreshResponse(access_token=access_token, expires_in=expires_in)


async def request_password_reset(email: str, db: AsyncSession) -> None:
    """
    Inicia el flujo de recuperación de contraseña.

    Genera un token de un solo uso, lo persiste con expiración
    en PostgreSQL, y notifica al usuario vía Notification Component.

    Nota de seguridad: aunque el usuario no exista, esta función
    retorna sin error para no exponer si el email está registrado
    (el router siempre responde con MessageResponse genérico).

    Parámetros
    ----------
    email : email_usuario enviado por la SPA.
    db    : sesión AsyncSession.
    """
    settings = get_settings()

    try:
        usuario = await _get_usuario_by_email(email, db)
    except UserNotFoundException:
        # Silencioso — no exponer si el email existe
        logger.info("Reset solicitado para email no registrado: %s", email)
        return

    # Token seguro de 48 caracteres URL-safe
    reset_token  = secrets.token_urlsafe(48)
    token_expiry = datetime.now(timezone.utc) + timedelta(
        minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
    )

    usuario.reset_token        = reset_token
    usuario.reset_token_expiry = token_expiry
    await db.commit()

    await _notify_reset_token(email, reset_token)

    logger.info(
        "Reset token generado | email=%s | expiry=%s",
        email,
        token_expiry.isoformat(),
    )


async def confirm_password_reset(payload: ResetPasswordConfirm, db: AsyncSession) -> None:
    """
    Confirma el cambio de contraseña con el token de recuperación.

    Flujo:
      1. Busca el usuario que tenga ese token activo en PostgreSQL.
      2. Verifica que el token no haya expirado.
      3. Hashea la nueva contraseña y la persiste.
      4. Invalida el token para que no pueda reutilizarse.

    Parámetros
    ----------
    payload : ResetPasswordConfirm con token y nueva_password validados.
    db      : sesión AsyncSession.

    Lanza
    -----
    ResetTokenInvalidException (400) si el token no existe o expiró.
    """
    result = await db.execute(
        select(Usuario).where(Usuario.reset_token == payload.token)
    )
    usuario = result.scalar_one_or_none()

    if usuario is None:
        raise ResetTokenInvalidException()

    # Verificar expiración
    if usuario.reset_token_expiry is None or datetime.now(timezone.utc) > usuario.reset_token_expiry.replace(tzinfo=timezone.utc):
        raise ResetTokenInvalidException(details="El token de recuperación expiró.")

    # Actualizar contraseña e invalidar token
    usuario.hash_password      = hash_password(payload.nueva_password)
    usuario.reset_token        = None
    usuario.reset_token_expiry = None
    await db.commit()

    logger.info("Contraseña actualizada exitosamente | email=%s", usuario.email_usuario)