from sqlalchemy import String, Float, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
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
    valor: Mapped[float] = mapped_column(Float)
