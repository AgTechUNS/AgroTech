from sqlalchemy import String, Float, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


"""class Base(DeclarativeBase):
    pass



class UsuarioModel(Base):
    __tablename__ = "usuarios"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(SAEnum("ADMIN", "AGRONOMO", "PRODUCTOR", name="rol_usuario"))


class CultivoModel(Base):
    __tablename__ = "cultivos"

    nombre: Mapped[str] = mapped_column(String(100), primary_key=True)
    umbral_humedad_minima: Mapped[float] = mapped_column(Float)
    umbral_temperatura_maxima: Mapped[float | None] = mapped_column(Float, nullable=True)


class CampoModel(Base): 
    __tablename__ = "campos"

    nombre: Mapped[str] = mapped_column(String(100), primary_key=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    coordenadas: Mapped[str] = mapped_column(Text, comment="GeoJSON Polygon")


class ParcelaModel(Base):
    __tablename__ = "parcelas"

    nombre: Mapped[str] = mapped_column(String(100), primary_key=True)
    campo_nombre: Mapped[str] = mapped_column(String(100), ForeignKey("campos.nombre"), primary_key=True)
    coordenadas: Mapped[str] = mapped_column(Text, comment="GeoJSON Polygon")
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    cultivo_nombre: Mapped[str | None] = mapped_column(String(100), ForeignKey("cultivos.nombre"), nullable=True)


class ReglaModel(Base):
    __tablename__ = "reglas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    metrica: Mapped[str] = mapped_column(String(50))
    operador: Mapped[str] = mapped_column(String(10))
    valor: Mapped[float] = mapped_column(Float)*/"""

class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(Enum("ADMIN", "AGRONOMO", "PRODUCTOR", name="rol_usuario"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    campos: Mapped[list["Campo"]] = relationship("Campo", back_populates="usuario", cascade="all, delete-orphan")
    alertas: Mapped[list["Alerta"]] = relationship("Alerta", back_populates="usuario", cascade="all, delete-orphan")


class Campo(Base):
    __tablename__ = "campo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coordenadas: Mapped[str] = mapped_column(Text, nullable=False, comment="Polígono GeoJSON")
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuario.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        UniqueConstraint("nombre", "usuario_id", name="uq_campo_nombre_usuario"),
    )

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="campos")
    parcelas: Mapped[list["Parcela"]] = relationship("Parcela", back_populates="campo", cascade="all, delete-orphan")
    sensores: Mapped[list["Sensor"]] = relationship("Sensor", back_populates="campo", cascade="all, delete-orphan")


class Parcela(Base):
    __tablename__ = "parcela"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coordenadas: Mapped[str] = mapped_column(Text, nullable=False, comment="Polígono GeoJSON")
    campo_id: Mapped[str] = mapped_column(String(36), ForeignKey("campo.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        UniqueConstraint("nombre", "campo_id", name="uq_parcela_nombre_campo"),
    )

    campo: Mapped["Campo"] = relationship("Campo", back_populates="parcelas")
    historiales_cultivo: Mapped[list["HistorialCultivo"]] = relationship(
        "HistorialCultivo", back_populates="parcela", cascade="all, delete-orphan"
    )
    sensores: Mapped[list["Sensor"]] = relationship("Sensor", back_populates="parcela", cascade="all, delete-orphan")
    predicciones: Mapped[list["Prediccion"]] = relationship("Prediccion", back_populates="parcela", cascade="all, delete-orphan")
    alertas: Mapped[list["Alerta"]] = relationship("Alerta", back_populates="parcela", cascade="all, delete-orphan")


class Cultivo(Base):
    __tablename__ = "cultivo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    nombre: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    umbral_humedad_minima: Mapped[float] = mapped_column(Float, nullable=False, comment="Constante agronómica: humedad mínima (%)")
    umbral_temperatura_maxima: Mapped[float] = mapped_column(Float, nullable=False, comment="Constante agronómica: temperatura máxima (°C)")
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    historiales: Mapped[list["HistorialCultivo"]] = relationship(
        "HistorialCultivo", back_populates="cultivo", cascade="all, delete-orphan"
    )


class HistorialCultivo(Base):
    __tablename__ = "historial_cultivo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    parcela_id: Mapped[str] = mapped_column(String(36), ForeignKey("parcela.id"), nullable=False)
    cultivo_id: Mapped[str] = mapped_column(String(36), ForeignKey("cultivo.id"), nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="NULL = cultivo actual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    parcela: Mapped["Parcela"] = relationship("Parcela", back_populates="historiales_cultivo")
    cultivo: Mapped["Cultivo"] = relationship("Cultivo", back_populates="historiales")


class Sensor(Base):
    __tablename__ = "sensor"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    sensor_id_externo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="ID del device en TTN/LoRaWAN")
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    ubicacion: Mapped[str] = mapped_column(Text, nullable=False, comment="Coordenadas absolutas GeoJSON Point o coordenadas relativas a la parcela")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parcela_id: Mapped[str] = mapped_column(String(36), ForeignKey("parcela.id"), nullable=False)
    campo_id: Mapped[str] = mapped_column(String(36), ForeignKey("campo.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    parcela: Mapped["Parcela"] = relationship("Parcela", back_populates="sensores")
    campo: Mapped["Campo"] = relationship("Campo", back_populates="sensores")


class Regla(Base):
    __tablename__ = "regla"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    metrica: Mapped[str] = mapped_column(String(50), nullable=False, comment="temperatura, humedad, ndvi")
    operador: Mapped[str] = mapped_column(String(10), nullable=False, comment=">=, <=, >, <, ==")
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Prediccion(Base):
    __tablename__ = "prediccion"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    parcela_id: Mapped[str] = mapped_column(String(36), ForeignKey("parcela.id"), nullable=False, index=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="Inicio de la ventana pronosticada")
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="Fin de la ventana pronosticada")
    resultado: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    parcela: Mapped["Parcela"] = relationship("Parcela", back_populates="predicciones")


class Alerta(Base):
    __tablename__ = "alerta"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    tipo: Mapped[str] = mapped_column(
        Enum("ALERTA_TIEMPO_REAL", "RECOMENDACION_BATCH", name="tipo_alerta"),
        nullable=False,
    )
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parcela_id: Mapped[str] = mapped_column(String(36), ForeignKey("parcela.id"), nullable=False, index=True)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuario.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    parcela: Mapped["Parcela"] = relationship("Parcela", back_populates="alertas")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="alertas")


class ImagenSatelital(Base):
    __tablename__ = "imagen_satelital"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    parcela_id: Mapped[str] = mapped_column(String(36), ForeignKey("parcela.id"), nullable=False, index=True)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ndvi: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Normalized Difference Vegetation Index (-1 a 1)")
    ndmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Normalized Difference Moisture Index (-1 a 1)")
    fuente: Mapped[str] = mapped_column(String(100), nullable=False, comment="Google Earth Engine, Sentinel Hub, etc.")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuario.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="SHA-256 del refresh token")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)



