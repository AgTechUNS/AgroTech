"""
models.py — Modelo SQLAlchemy de la entidad USUARIO.

Refleja el Diccionario de Datos centralizado definido por el equipo AgTechUNS.
El Relational Repository es el único componente que escribe/lee esta tabla —
este modelo es la representación Python de ese contrato compartido.

Tabla: usuarios
PK natural: email_usuario

Relaciones:
  - USUARIO ←→ ROL ←→ CAMPO  (tabla de asociación usuario_rol_campo)
    Un usuario puede tener distintos roles sobre distintos campos.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, ForeignKey, Uuid, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.enums import RoleEnum


# ──────────────────────────────────────────────
# Base declarativa compartida
# ──────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────
# Tabla de asociación USUARIO — ROL — CAMPO
# ──────────────────────────────────────────────

class UsuarioRolCampo(Base):
    """
    Tabla de asociación que vincula un usuario con un rol
    sobre un campo agrícola específico.

    Definida en el modelo compartido del equipo como USUARIO-ROL-CAMPO.
    El campo_id referencia la tabla de campos del módulo de parcelas
    (gestionada por otro compañero del equipo).
    """

    __tablename__ = "usuario_rol_campo"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email_usuario: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("usuarios.email_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    rol: Mapped[RoleEnum] = mapped_column(
        SAEnum(RoleEnum, native_enum=False),
        nullable=False,
    )
    # campo_id referencia la tabla del módulo de parcelas (FK cross-módulo)
    campo_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )

    # Relación inversa
    usuario: Mapped["Usuario"] = relationship(back_populates="roles_campos")


# ──────────────────────────────────────────────
# Entidad principal: USUARIO
# ──────────────────────────────────────────────

class Usuario(Base):
    """
    Entidad USUARIO — Diccionario de Datos AgTechUNS.

    Atributos obligatorios definidos por el equipo:
      - email_usuario  : PK natural, identificador único del usuario.
      - nombre         : nombre completo.
      - telefono       : teléfono de contacto.
      - hash_password  : hash bcrypt generado por core/hashing.py.

    Atributos de gestión (agregados por este módulo):
      - is_active          : permite deshabilitar usuarios sin borrarlos.
      - reset_token        : token temporal para recuperación de contraseña.
      - reset_token_expiry : expiración del token de recuperación.
      - created_at         : auditoría de creación.
      - updated_at         : auditoría de última modificación.
    """

    __tablename__ = "usuarios"

    # ── Atributos del diccionario de datos compartido ──
    email_usuario: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    telefono: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    hash_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hash bcrypt generado por core/hashing.hash_password()",
    )

    # ── Atributos de gestión del módulo auth ──
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="False = usuario deshabilitado, no puede iniciar sesión.",
    )
    reset_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        comment="Token temporal para recuperación de contraseña.",
    )
    reset_token_expiry: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Expiración del reset_token. Validado en auth/service.py.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relación con tabla de asociación ──
    roles_campos: Mapped[list["UsuarioRolCampo"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Usuario email={self.email_usuario} active={self.is_active}>"