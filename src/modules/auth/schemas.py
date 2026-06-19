"""
schemas.py — Schemas Pydantic para los endpoints del módulo auth/.

Todos los schemas heredan de BaseSchema, que configura:
  - camelCase hacia el cliente (alias_generator)
  - snake_case internamente (populate_by_name)
  - strip de espacios en strings

Contratos de entrada y salida:
  - POST /auth/login          : LoginRequest → TokenResponse
  - POST /auth/reset-request  : ResetRequest → MessageResponse
  - POST /auth/reset-confirm  : ResetConfirm → MessageResponse
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

from modules.security.core.enums import RoleEnum
from pydantic.alias_generators import to_camel


# ──────────────────────────────────────────────
# Base — Punto Único de configuración de contratos
# ──────────────────────────────────────────────

class BaseSchema(BaseModel):
    """
    Base compartida para todos los schemas de AgTechUNS.

    Garantiza uniformidad en toda la comunicación con la SPA:
      - camelCase en JSON (emailUsuario, nuevaPassword...)
      - snake_case internamente (email_usuario, nueva_password...)
      - Espacios eliminados automáticamente en strings

    Uso:
        class MiSchema(BaseSchema):
            email_usuario: str   # → "emailUsuario" en JSON
    """

    model_config = {
        "alias_generator": to_camel,       # snake → camelCase en JSON
        "populate_by_name": True,          # permite usar snake_case internamente
        "str_strip_whitespace": True,      # elimina espacios al inicio/fin
        "from_attributes": True,           # permite construir desde ORM (SQLAlchemy)
    }


# ──────────────────────────────────────────────
# Request schemas — entrada del cliente
# ──────────────────────────────────────────────

class LoginRequest(BaseSchema):
    """
    Cuerpo del POST /auth/login.

    JSON esperado:
        { "emailUsuario": "...", "password": "..." }
    """

    email_usuario: EmailStr = Field(
        ...,
        description="Email del usuario. Es la clave primaria natural del sistema.",
        examples=["agronomo@agtech.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Contraseña en texto plano. Nunca se almacena.",
        examples=["mi_clave_segura"],
    )


class ResetPasswordRequest(BaseSchema):
    """
    Cuerpo del POST /auth/reset-request.

    Inicia el flujo de recuperación. Solo requiere el email para
    que el Notification Component envíe el token al usuario.

    JSON esperado:
        { "emailUsuario": "..." }
    """

    email_usuario: EmailStr = Field(
        ...,
        description="Email del usuario que solicita recuperar su contraseña.",
        examples=["agronomo@agtech.com"],
    )


class ResetPasswordConfirm(BaseSchema):
    """
    Cuerpo del POST /auth/reset-confirm.

    Completa el flujo de recuperación. El token es de un solo uso
    y nueva_password será hasheada por core/hashing antes de persistirse.

    JSON esperado:
        { "token": "...", "nuevaPassword": "...", "confirmarPassword": "..." }
    """

    token: str = Field(
        ...,
        min_length=32,
        description="Token de un solo uso recibido por email.",
    )
    nueva_password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Nueva contraseña en texto plano.",
    )
    confirmar_password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Confirmación de la nueva contraseña. Debe coincidir con nuevaPassword.",
    )

    @field_validator("confirmar_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "nueva_password" in info.data and v != info.data["nueva_password"]:
            raise ValueError("Las contraseñas no coinciden.")
        return v


# ──────────────────────────────────────────────
# Response schemas — salida hacia el cliente
# ──────────────────────────────────────────────

class TokenResponse(BaseSchema):
    """
    Respuesta del POST /auth/login exitoso.

    El JWT codifica internamente: emailUsuario (sub), rol y campos asignados.
    El cliente debe enviarlo como: Authorization: Bearer <accessToken>

    JSON devuelto:
        {
            "accessToken": "...",
            "refreshToken": "...",
            "tokenType": "bearer",
            "expiresIn": 900
        }
    """

    access_token: str = Field(
        ...,
        description="JWT de acceso. Expira según ACCESS_TOKEN_EXPIRE_MINUTES.",
    )
    refresh_token: str = Field(
        ...,
        description="JWT de renovación. Expira según REFRESH_TOKEN_EXPIRE_DAYS.",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token. Siempre 'bearer'.",
    )
    expires_in: int = Field(
        ...,
        description="Segundos hasta la expiración del access_token.",
    )


class RefreshRequest(BaseSchema):
    """
    Cuerpo del POST /auth/refresh.

    JSON esperado:
        { "refreshToken": "..." }
    """

    refresh_token: str = Field(
        ...,
        min_length=10,
        description="JWT de renovación emitido en el login.",
    )


class RefreshResponse(BaseSchema):
    """
    Respuesta del POST /auth/refresh exitoso.

    Solo retorna un nuevo access token — no un nuevo refresh token.

    JSON devuelto:
        { "accessToken": "...", "expiresIn": 900 }
    """

    access_token: str = Field(
        ...,
        description="Nuevo JWT de acceso. Expira según ACCESS_TOKEN_EXPIRE_MINUTES.",
    )
    expires_in: int = Field(
        ...,
        description="Segundos hasta la expiración del nuevo access_token.",
    )


class MessageResponse(BaseSchema):
    """
    Respuesta genérica para operaciones sin datos sensibles.

    Usada en reset-request y reset-confirm para no exponer
    si un email existe o no en el sistema (anti-enumeración).

    JSON devuelto:
        { "message": "..." }
    """

    message: str = Field(
        ...,
        description="Mensaje informativo para el cliente.",
        examples=["Si el email existe en el sistema, recibirás las instrucciones."],
    )


# ──────────────────────────────────────────────
# Schemas internos — entre capas, nunca al exterior
# ──────────────────────────────────────────────

class UsuarioContext(BaseSchema):
    """
    Representación interna del usuario autenticado.
    Construida por auth/service.py para emitir el JWT.

    No se expone al cliente — su contenido viaja
    codificado dentro del token.
    """

    email_usuario: str
    nombre: str
    rol: RoleEnum
    campos: list[str] = Field(
        default_factory=list,
        description="IDs de los campos asignados al usuario.",
    )
    is_active: bool


class UsuarioPublico(BaseSchema):
    """
    Proyección pública del usuario para endpoints de perfil.
    Nunca incluye hash_password ni tokens internos.

    JSON devuelto:
        {
            "emailUsuario": "...",
            "nombre": "...",
            "telefono": "...",
            "rol": "...",
            "createdAt": "..."
        }
    """

    email_usuario: str
    nombre: str
    telefono: str
    rol: RoleEnum
    created_at: datetime