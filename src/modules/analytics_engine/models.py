from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class AlertaRecomendacion(BaseModel):
    tipo: Literal["ALERTA_TIEMPO_REAL", "RECOMENDACION_BATCH"]
    fechaEmision: datetime
    mensaje: str
    nombreParcela: str
    emailUsuario: EmailStr | None = None


class Prediccion(BaseModel):
    fechaEmision: datetime
    resultado: str
    fechaIni: datetime
    fechaFin: datetime


class Paginacion(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int


class RecomendacionesResponse(BaseModel):
    data: list[AlertaRecomendacion]
    pagination: Paginacion


class PrediccionesResponse(BaseModel):
    data: list[Prediccion]
    pagination: Paginacion
