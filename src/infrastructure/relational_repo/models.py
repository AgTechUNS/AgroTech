from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuario"

    email_usuario: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<Usuario {self.email_usuario!r}>"


class Campo(Base):
    __tablename__ = "campo"

    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    coordenadas_campo: Mapped[str] = mapped_column(Text, nullable=False, comment="Poligono GeoJSON")
    descripcion_campo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Campo {self.nombre_campo!r}>"


class Rol(Base):
    __tablename__ = "rol"

    nombre_rol: Mapped[str] = mapped_column(String(100), primary_key=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Rol {self.nombre_rol!r}>"


class Cultivo(Base):
    __tablename__ = "cultivo"

    nombre_cultivo: Mapped[str] = mapped_column(String(255), primary_key=True)
    variedad: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f"<Cultivo {self.nombre_cultivo!r}>"


class Sensor(Base):
    __tablename__ = "sensor"

    nombre_codigo_sensor: Mapped[str] = mapped_column(String(255), primary_key=True)
    estado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="True=activo, False=inactivo")

    def __repr__(self):
        return f"<Sensor {self.nombre_codigo_sensor!r} activo={self.estado}>"


class ImagenSatelital(Base):
    __tablename__ = "imagen_satelital"

    id_imagen: Mapped[str] = mapped_column(String(255), primary_key=True)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    proveedor: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<ImagenSatelital {self.id_imagen!r}>"


class EjecucionBatch(Base):
    __tablename__ = "ejecucion_batch"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, comment="EN_CURSO, COMPLETADO, FALLIDO")
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<EjecucionBatch {self.fecha_ini.isoformat()} estado={self.estado}>"


class Parcela(Base):
    __tablename__ = "parcela"

    nombre_parcela: Mapped[str] = mapped_column(String(255), primary_key=True)
    coordenadas_parcela: Mapped[str] = mapped_column(Text, nullable=False, comment="Poligono GeoJSON")
    descripcion_parcela: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"), nullable=False)

    campo: Mapped["Campo"] = relationship("Campo")

    def __repr__(self):
        return f"<Parcela {self.nombre_parcela!r} en {self.nombre_campo!r}>"


class Regla(Base):
    __tablename__ = "regla"

    nombre_regla: Mapped[str] = mapped_column(String(255), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    formula: Mapped[str] = mapped_column(Text, nullable=False, comment="Expresion de la regla agroclim├ítica")
    descripcion_regla: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    umbral: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(["nombre_campo"], ["campo.nombre_campo"]),
    )

    def __repr__(self):
        return f"<Regla {self.nombre_regla!r} umbral={self.umbral}>"


class VentanaTemporal(Base):
    __tablename__ = "ventana_temporal"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), nullable=False)

    parcela: Mapped["Parcela"] = relationship("Parcela")

    def __repr__(self):
        return f"<VentanaTemporal {self.fecha_ini.isoformat()} - {self.fecha_fin.isoformat()}>"


class Alerta(Base):
    __tablename__ = "alerta"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    nombre_parcela: Mapped[str] = mapped_column(String(255), nullable=False)
    email_usuario: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f"<Alerta #{self.id} parcela={self.nombre_parcela!r}>"


class UsuarioRolCampo(Base):
    __tablename__ = "usuario_rol_campo"

    email_usuario: Mapped[str] = mapped_column(String(255), ForeignKey("usuario.email_usuario"), primary_key=True)
    nombre_rol: Mapped[str] = mapped_column(String(100), ForeignKey("rol.nombre_rol"), primary_key=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"), primary_key=True)

    usuario: Mapped["Usuario"] = relationship("Usuario")
    rol: Mapped["Rol"] = relationship("Rol")
    campo: Mapped["Campo"] = relationship("Campo")

    def __repr__(self):
        return f"<UsuarioRolCampo {self.email_usuario} / {self.nombre_rol} / {self.nombre_campo}>"


class ParcelaImagenSatelital(Base):
    __tablename__ = "parcela_imagen_satelital"

    id_imagen: Mapped[str] = mapped_column(String(255), ForeignKey("imagen_satelital.id_imagen"), primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True)
    indice_ndvi: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Normalized Difference Vegetation Index (-1 a 1)")
    indice_ndmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Normalized Difference Moisture Index (-1 a 1)")

    imagen: Mapped["ImagenSatelital"] = relationship("ImagenSatelital")
    parcela: Mapped["Parcela"] = relationship("Parcela")

    def __repr__(self):
        return f"<ParcelaImagenSatelital {self.id_imagen} / {self.nombre_parcela}>"


class RegistroCultivo(Base):
    __tablename__ = "registro_cultivo"

    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True)
    nombre_cultivo: Mapped[str] = mapped_column(String(255), ForeignKey("cultivo.nombre_cultivo"), primary_key=True)
    fecha_siembra: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    fecha_cosecha: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    parcela: Mapped["Parcela"] = relationship("Parcela")
    cultivo: Mapped["Cultivo"] = relationship("Cultivo")

    def __repr__(self):
        return f"<RegistroCultivo {self.nombre_parcela} / {self.nombre_cultivo}>"


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

    def __repr__(self):
        return f"<SensorParcela {self.nombre_codigo_sensor} / {self.nombre_parcela}>"


class Prediccion(Base):
    __tablename__ = "prediccion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resultado: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_ini: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    nombre_regla: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nombre_campo: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<Prediccion #{self.id} campo={self.nombre_campo!r}>"
