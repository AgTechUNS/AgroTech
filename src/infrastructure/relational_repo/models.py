from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────
# Entidades Independientes
# ──────────────────────────────────────────────


class Usuario(Base):
    __tablename__ = "usuario"

    email_usuario: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)


class Campo(Base):
    __tablename__ = "campo"

    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    coordenadas_campo: Mapped[str] = mapped_column(Text, nullable=False, comment="Polígono GeoJSON")
    descripcion_campo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Rol(Base):
    __tablename__ = "rol"

    nombre_rol: Mapped[str] = mapped_column(String(100), primary_key=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Cultivo(Base):
    __tablename__ = "cultivo"

    nombre_cultivo: Mapped[str] = mapped_column(String(255), primary_key=True)
    variedad: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Sensor(Base):
    __tablename__ = "sensor"

    nombre_codigo_sensor: Mapped[str] = mapped_column(String(255), primary_key=True)
    estado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="True=activo, False=inactivo")


class ImagenSatelital(Base):
    __tablename__ = "imagen_satelital"

    id_imagen: Mapped[str] = mapped_column(String(255), primary_key=True)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    proveedor: Mapped[str] = mapped_column(String(255), nullable=False)


class EjecucionBatch(Base):
    __tablename__ = "ejecucion_batch"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, comment="EN_CURSO, COMPLETADO, FALLIDO")
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# ──────────────────────────────────────────────
# Entidades Dependientes (Jerárquicas)
# ──────────────────────────────────────────────


class Parcela(Base):
    __tablename__ = "parcela"

    nombre_parcela: Mapped[str] = mapped_column(String(255), primary_key=True)
    coordenadas_parcela: Mapped[str] = mapped_column(Text, nullable=False, comment="Polígono GeoJSON")
    descripcion_parcela: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"), nullable=False)

    campo: Mapped["Campo"] = relationship("Campo")


class Regla(Base):
    __tablename__ = "regla"

    nombre_regla: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    formula: Mapped[str] = mapped_column(Text, nullable=False, comment="Expresión de la regla agroclimática")
    descripcion_regla: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    umbral: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["nombre_campo"],
            ["campo.nombre_campo"],
        ),
    )


class VentanaTemporal(Base):
    __tablename__ = "ventana_temporal"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), nullable=False)

    parcela: Mapped["Parcela"] = relationship("Parcela")


class Alerta(Base):
    __tablename__ = "alerta"


    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), nullable=False)
    email_usuario: Mapped[str] = mapped_column(String(255), ForeignKey("usuario.email_usuario"), nullable=False)

    parcela: Mapped["Parcela"] = relationship("Parcela")
    usuario: Mapped["Usuario"] = relationship("Usuario")


# ──────────────────────────────────────────────
# Asociaciones (Tablas Intermedias M:N)
# ──────────────────────────────────────────────


class UsuarioRolCampo(Base):
    __tablename__ = "usuario_rol_campo"

    email_usuario: Mapped[str] = mapped_column(String(255), ForeignKey("usuario.email_usuario"), primary_key=True)
    nombre_rol: Mapped[str] = mapped_column(String(100), ForeignKey("rol.nombre_rol"), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"), primary_key=True)

    usuario: Mapped["Usuario"] = relationship("Usuario")
    rol: Mapped["Rol"] = relationship("Rol")
    campo: Mapped["Campo"] = relationship("Campo")


class ParcelaImagenSatelital(Base):
    __tablename__ = "parcela_imagen_satelital"

    id_imagen: Mapped[str] = mapped_column(String(255), ForeignKey("imagen_satelital.id_imagen"), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True)
    indice_ndvi: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Normalized Difference Vegetation Index (-1 a 1)")
    indice_ndmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Normalized Difference Moisture Index (-1 a 1)")

    imagen: Mapped["ImagenSatelital"] = relationship("ImagenSatelital")
    parcela: Mapped["Parcela"] = relationship("Parcela")


class RegistroCultivo(Base):
    __tablename__ = "registro_cultivo"

    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True)
    nombre_cultivo: Mapped[str] = mapped_column(String(255), ForeignKey("cultivo.nombre_cultivo"), primary_key=True)
    fecha_siembra: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    fecha_cosecha: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    parcela: Mapped["Parcela"] = relationship("Parcela")
    cultivo: Mapped["Cultivo"] = relationship("Cultivo")


class SensorParcela(Base):
    __tablename__ = "sensor_parcela"

    nombre_codigo_sensor: Mapped[str] = mapped_column(String(255), ForeignKey("sensor.nombre_codigo_sensor"), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"), nullable=False)
    fecha_instalacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    fecha_retiro: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sensor: Mapped["Sensor"] = relationship("Sensor")
    parcela: Mapped["Parcela"] = relationship("Parcela")
    campo: Mapped["Campo"] = relationship("Campo")


class Prediccion(Base):
    __tablename__ = "prediccion"
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resultado: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    nombre_regla: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_campo: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["nombre_regla", "nombre_campo"],
            ["regla.nombre_regla", "regla.nombre_campo"],
        ),
        ForeignKeyConstraint(
            ["fecha_ini", "fecha_fin"],
            ["ventana_temporal.fecha_ini", "ventana_temporal.fecha_fin"],
        ),
    )
