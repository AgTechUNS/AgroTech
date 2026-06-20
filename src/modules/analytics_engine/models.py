from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


# ──────────────────────────────────────────────
# Tipos compartidos para el motor de reglas
# ──────────────────────────────────────────────

TipoRegla = Literal["helada", "sequia", "calor_extremo", "anomalia_humedad", "lluvia_intensa"]
OperadorComparacion = Literal["<", ">", "<=", ">=", "=="]
MetricaAgregacion = Literal["promedio", "maximo", "minimo"]
NivelAlerta = Literal["verde", "amarillo", "rojo"]


@dataclass
class ReglaEvaluacion:
    tipo: TipoRegla
    campo_id: str
    parcela_id: str | None = None
    umbral: float = 0.0
    ventana_minutos: int = 60
    operador: OperadorComparacion = "<"
    metrica: MetricaAgregacion = "promedio"
    campo_telemetria: str = "temperatura"
    habilitada: bool = True


@dataclass
class ResultadoPrediccion:
    regla: ReglaEvaluacion
    campo_id: str
    parcela_id: str | None
    timestamp: datetime
    valor_calculado: float
    nivel_alerta: NivelAlerta
    mensaje: str
    lecturas_consideradas: int = 0


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


# ──────────────────────────────────────────────
# Esquemas para CRUD de reglas (Fase 4)
# ──────────────────────────────────────────────


class ReglaRequest(BaseModel):
    nombre_regla: str
    nombre_campo: str
    metrica: str
    operador: str
    valor: float
    descripcion: str | None = None


class ReglaResponse(BaseModel):
    nombre_regla: str
    nombre_campo: str
    metrica: str
    operador: str
    valor: float
    descripcion: str | None = None


class ReglaUpdateRequest(BaseModel):
    metrica: str | None = None
    operador: str | None = None
    valor: float | None = None
    descripcion: str | None = None
