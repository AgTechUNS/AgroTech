import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Usuario ─────────────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"

    email_usuario: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(50), nullable=False, comment="ADMIN | AGRONOMO | PRODUCTOR")
    admin_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)


# ── Campo ───────────────────────────────────────────────────────────

class Campo(Base):
    __tablename__ = "campos"

    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    descripcion_campo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coordenadas_campo: Mapped[str] = mapped_column(Text, nullable=False, comment="Poligono GeoJSON")
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)


# ── Parcela ─────────────────────────────────────────────────────────

class Parcela(Base):
    __tablename__ = "parcelas"

    nombre_parcela: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campos.nombre_campo"), primary_key=True)
    descripcion_parcela: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nombre_cultivo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    variedad: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    coordenadas_parcela: Mapped[str] = mapped_column(Text, nullable=False, comment="Poligono GeoJSON")
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)

    campo: Mapped["Campo"] = relationship("Campo")


# ── Cultivo ─────────────────────────────────────────────────────────

class Cultivo(Base):
    __tablename__ = "cultivos"

    nombre_cultivo: Mapped[str] = mapped_column(String(255), primary_key=True)
    variedad: Mapped[str] = mapped_column(String(255), primary_key=True)
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)


# ── Regla ───────────────────────────────────────────────────────────

class Regla(Base):
    __tablename__ = "reglas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrica: Mapped[str] = mapped_column(String(100), nullable=False)
    operador: Mapped[str] = mapped_column(String(10), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)
    campos_asignados: Mapped[str] = mapped_column(Text, nullable=False, default="[]", comment="JSON array de nombres de campo")


# ── Sensor ──────────────────────────────────────────────────────────

class Sensor(Base):
    __tablename__ = "sensores"

    device_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_parcela: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, comment="temperatura_humedad | ph | lluvia")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)


# ── Alerta ──────────────────────────────────────────────────────────

class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    nombre_parcela: Mapped[str] = mapped_column(String(255), nullable=False)
    email_usuario: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


# ── Prediccion ──────────────────────────────────────────────────────

class Prediccion(Base):
    __tablename__ = "predicciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resultado: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    nombre_regla: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), nullable=False)


# ── Imagen Satelital ────────────────────────────────────────────────

class ImagenSatelital(Base):
    __tablename__ = "imagenes_satelitales"

    id_imagen: Mapped[str] = mapped_column(String(255), primary_key=True)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    proveedor: Mapped[str] = mapped_column(String(255), nullable=False)


# ── Parcela-Imagen Satelital ────────────────────────────────────────

class ParcelaImagenSatelital(Base):
    __tablename__ = "parcelas_imagenes_satelitales"

    id_imagen: Mapped[str] = mapped_column(String(255), ForeignKey("imagenes_satelitales.id_imagen"), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    indice_ndvi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    indice_ndmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    imagen: Mapped["ImagenSatelital"] = relationship(lazy="joined")


# ── Ejecucion Batch ─────────────────────────────────────────────────

class EjecucionBatch(Base):
    __tablename__ = "ejecuciones_batch"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, comment="EN_CURSO | COMPLETADO | FALLIDO")
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Ventana Temporal ────────────────────────────────────────────────

class VentanaTemporal(Base):
    __tablename__ = "ventanas_temporales"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), nullable=False)
