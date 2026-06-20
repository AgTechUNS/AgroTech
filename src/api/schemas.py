"""Schemas Pydantic (DTOs de la API): contrato de entrada/salida en JSON.

Implementan la responsabilidad de "Validación de Entrada" del API Controller,
incluida la validación de polígono del CU-03 (INT-01).
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

Coordenada = list[float]  # [longitud, latitud]


# ---------- Campos ----------
class CampoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nombre: str
    propietario_id: str


class CampoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)


# ---------- Cultivos ----------
class CultivoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nombre: str


class CultivoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)


# ---------- Parcelas ----------
class ParcelaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nombre: str
    campo_id: str
    cultivo_id: str | None = None
    poligono: list[Coordenada]


class ParcelaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    campo_id: str
    cultivo_id: str | None = None
    poligono: list[Coordenada] = Field(min_length=3)

    @field_validator("poligono")
    @classmethod
    def _validar_poligono(cls, v: list[Coordenada]) -> list[Coordenada]:
        for punto in v:
            if len(punto) != 2:
                raise ValueError("Cada coordenada debe ser [longitud, latitud].")
            lon, lat = punto
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                raise ValueError("Coordenada fuera de rango (lon[-180,180], lat[-90,90]).")
        if v[0] != v[-1]:           # CU-03: cerrar el anillo si no viene cerrado
            v = v + [v[0]]
        if len(v) < 4:
            raise ValueError("Un polígono requiere al menos 3 vértices distintos.")
        return v


# ---------- Estado de parcela (CU-01) ----------
class LecturaOut(BaseModel):
    humedad: float
    temperatura: float
    timestamp: datetime


class EstadoParcelaOut(BaseModel):
    parcela_id: str
    nombre: str
    ultima_lectura: LecturaOut | None = None
    alerta: str | None = None


# ---------- Predicciones (CU-08) ----------
class PrediccionOut(BaseModel):
    parcela_id: str
    necesidad_riego: str
    necesidad_fertilizacion: str
    ndvi: float
    generada_en: datetime


# ---------- Reportes (CU-06) ----------
class ReporteOut(BaseModel):
    campo_id: str
    resumen: str
    generado_en: datetime
    parcelas: list[str]
