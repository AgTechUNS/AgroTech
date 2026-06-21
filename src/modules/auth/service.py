import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.models import Usuario
from modules.auth.schemas import RefreshResponse, ResetPasswordConfirm, TokenResponse
from modules.security.core.config import get_settings
from modules.security.core.enums import RoleEnum
from modules.security.core.exceptions import (
    InvalidCredentialsException,
    ResetTokenInvalidException,
    UserNotFoundException,
)
from modules.security.core.hashing import hash_password, needs_rehash, verify_password
from modules.security.schemas import UserContext
from modules.security.token_service import create_access_token, create_refresh_token, decode_token

logger = logging.getLogger(__name__)


async def _get_usuario_by_email(email: str, db: AsyncSession) -> Usuario:
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
    return UserContext(
        user_id=usuario.email_usuario,
        role=RoleEnum(usuario.rol),
        assigned_fields=[],
    )


async def _notify_reset_token(email: str, token: str) -> None:
    settings = get_settings()
    if settings.NOTIFICATION_SERVICE_URL:
        logger.info("STUB Notification | Llamar a %s con token para %s", settings.NOTIFICATION_SERVICE_URL, email)
    else:
        logger.warning("DESARROLLO — Reset token para %s: %s", email, token)


async def verify_credentials(email: str, password: str, db: AsyncSession) -> Usuario:
    try:
        usuario = await _get_usuario_by_email(email, db)
    except UserNotFoundException:
        raise InvalidCredentialsException()

    if not verify_password(password, usuario.hash_password):
        logger.warning("Credenciales inválidas | email=%s", email)
        raise InvalidCredentialsException()

    if needs_rehash(usuario.hash_password):
        usuario.hash_password = hash_password(password)
        await db.commit()
        logger.info("Hash bcrypt actualizado | email=%s", email)

    return usuario


def build_token_response(usuario: Usuario) -> TokenResponse:
    user_context = _build_user_context(usuario)
    access_token, expires_in = create_access_token(user_context)
    refresh_token = create_refresh_token(user_context)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> RefreshResponse:
    partial_context = decode_token(refresh_token, expected_type="refresh")
    usuario = await _get_usuario_by_email(partial_context.user_id, db)
    user_context = _build_user_context(usuario)
    access_token, expires_in = create_access_token(user_context)
    logger.info("Access token renovado | user=%s | role=%s", user_context.user_id, user_context.role.value)
    return RefreshResponse(access_token=access_token, expires_in=expires_in)


async def request_password_reset(email: str, db: AsyncSession) -> None:
    settings = get_settings()
    try:
        usuario = await _get_usuario_by_email(email, db)
    except UserNotFoundException:
        logger.info("Reset solicitado para email no registrado: %s", email)
        return

    reset_token = secrets.token_urlsafe(48)
    token_expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)

    usuario.reset_token = reset_token
    usuario.reset_token_expiry = token_expiry
    await db.commit()

    await _notify_reset_token(email, reset_token)
    logger.info("Reset token generado | email=%s | expiry=%s", email, token_expiry.isoformat())


async def confirm_password_reset(payload: ResetPasswordConfirm, db: AsyncSession) -> None:
    result = await db.execute(
        select(Usuario).where(Usuario.reset_token == payload.token)
    )
    usuario = result.scalar_one_or_none()
    if usuario is None:
        raise ResetTokenInvalidException()

    if usuario.reset_token_expiry is None or datetime.now(timezone.utc) > usuario.reset_token_expiry.replace(tzinfo=timezone.utc):
        raise ResetTokenInvalidException(details="El token de recuperación expiró.")

    usuario.hash_password = hash_password(payload.nueva_password)
    usuario.reset_token = None
    usuario.reset_token_expiry = None
    await db.commit()
    logger.info("Contraseña actualizada exitosamente | email=%s", usuario.email_usuario)
