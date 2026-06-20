from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Modelos de dominio internos (dataclasses)
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


# ──────────────────────────────────────────────
# Esquemas Pydantic para la API REST
# ──────────────────────────────────────────────


class ReglaRequest(BaseModel):
    tipo: TipoRegla
    campo_id: str = Field(..., min_length=1)
    parcela_id: str | None = None
    umbral: float
    ventana_minutos: int = Field(default=60, ge=1, le=1440)
    operador: OperadorComparacion = "<"
    metrica: MetricaAgregacion = "promedio"
    campo_telemetria: str = "temperatura"
    habilitada: bool = True


class ReglaResponse(BaseModel):
    id: str
    tipo: TipoRegla
    campo_id: str
    parcela_id: str | None
    umbral: float
    ventana_minutos: int
    operador: OperadorComparacion
    metrica: MetricaAgregacion
    campo_telemetria: str
    habilitada: bool


class PrediccionResponse(BaseModel):
    regla_id: str
    tipo: TipoRegla
    campo_id: str
    parcela_id: str | None
    timestamp: datetime
    valor_calculado: float
    nivel_alerta: NivelAlerta
    mensaje: str
    lecturas_consideradas: int


class HealthResponse(BaseModel):
    estado: Literal["ok", " degradado"] = "ok"
    reglas_cargadas: int = 0
    ultima_ejecucion: datetime | None = None
