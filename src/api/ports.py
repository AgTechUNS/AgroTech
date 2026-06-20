"""Puertos (contratos) de los que depende el API Controller.

El API Controller NO conoce implementaciones concretas: depende solo de estos
Protocols. Esto permite desarrollarlo y testearlo de forma aislada y enchufar
los componentes reales (Relational Repository, Time Series Repository,
Analytics Engine) sin modificar ni un endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable


class Rol(str, Enum):
    ADMINISTRADOR = "Administrador"
    AGRONOMO = "Agrónomo"


@dataclass(frozen=True)
class SecurityContext:
    """Contexto inyectado por el Security Controller tras validar el JWT."""
    user_id: str
    rol: Rol
    campos_asignados: tuple[str, ...] = ()

    @property
    def es_admin(self) -> bool:
        return self.rol is Rol.ADMINISTRADOR


# --- DTOs de dominio que devuelven los componentes/repositorios -----------
@dataclass
class CampoDTO:
    id: str
    nombre: str
    propietario_id: str


@dataclass
class ParcelaDTO:
    id: str
    nombre: str
    campo_id: str
    cultivo_id: str | None
    poligono: list[list[float]]


@dataclass
class CultivoDTO:
    id: str
    nombre: str


@dataclass
class LecturaDTO:
    parcela_id: str
    humedad: float
    temperatura: float
    timestamp: datetime


@dataclass
class PrediccionDTO:
    parcela_id: str
    necesidad_riego: str
    necesidad_fertilizacion: str
    ndvi: float
    generada_en: datetime


@dataclass
class ReporteDTO:
    campo_id: str
    resumen: str
    generado_en: datetime
    parcelas: list[str]


@runtime_checkable
class RelationalRepositoryPort(Protocol):
    async def listar_campos(self) -> list[CampoDTO]: ...
    async def obtener_campo(self, campo_id: str) -> CampoDTO | None: ...
    async def crear_campo(self, nombre: str, propietario_id: str) -> CampoDTO: ...
    async def listar_parcelas(self, campo_id: str | None = None) -> list[ParcelaDTO]: ...
    async def obtener_parcela(self, parcela_id: str) -> ParcelaDTO | None: ...
    async def crear_parcela(self, nombre: str, campo_id: str,
                            cultivo_id: str | None, poligono: list[list[float]]) -> ParcelaDTO: ...
    async def listar_cultivos(self) -> list[CultivoDTO]: ...
    async def crear_cultivo(self, nombre: str) -> CultivoDTO: ...


@runtime_checkable
class TimeSeriesRepositoryPort(Protocol):
    async def ultima_lectura(self, parcela_id: str) -> LecturaDTO | None: ...


@runtime_checkable
class AnalyticsEnginePort(Protocol):
    async def predicciones(self, parcela_id: str) -> PrediccionDTO | None: ...
    async def reporte_campo(self, campo_id: str, parcela_ids: list[str]) -> ReporteDTO: ...
