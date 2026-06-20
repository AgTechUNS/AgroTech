"""Adaptadores MOCK en memoria — STUB temporal.

El API Controller depende solo de los Ports, por eso estos mocks se pueden
reemplazar por los componentes reales SIN tocar los controllers:
  - RelationalRepository -> src/infrastructure/relational_repo
        (rama RelationalRepository2: SQLAlchemy / PostgreSQL)
  - TimeSeriesRepository -> src/infrastructure/time_series_repo (InfluxDB)
  - AnalyticsEngine      -> src/modules/analytics_engine/engine.py
Hasta entonces, sirven datos de demostración para poder ejecutar y probar.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .ports import (CampoDTO, CultivoDTO, LecturaDTO, ParcelaDTO,
                    PrediccionDTO, ReporteDTO)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class _Store:
    def __init__(self) -> None:
        self.campos = {
            "c1": CampoDTO("c1", "La Esperanza", "u-admin"),
            "c2": CampoDTO("c2", "El Triunfo", "u-admin"),
        }
        self.cultivos = {
            "cu1": CultivoDTO("cu1", "Soja"),
            "cu2": CultivoDTO("cu2", "Trigo"),
            "cu3": CultivoDTO("cu3", "Maíz"),
        }
        self.parcelas = {
            "p1": ParcelaDTO("p1", "Lote 1", "c1", "cu1",
                             [[-62.27, -38.72], [-62.26, -38.72], [-62.26, -38.71],
                              [-62.27, -38.71], [-62.27, -38.72]]),
            "p2": ParcelaDTO("p2", "Lote 4", "c1", "cu2",
                             [[-62.25, -38.73], [-62.24, -38.73], [-62.24, -38.72],
                              [-62.25, -38.72], [-62.25, -38.73]]),
            "p3": ParcelaDTO("p3", "Lote 7", "c2", "cu3",
                             [[-62.30, -38.70], [-62.29, -38.70], [-62.29, -38.69],
                              [-62.30, -38.69], [-62.30, -38.70]]),
        }
        self._seq = 100

    def next_id(self, prefijo: str) -> str:
        self._seq += 1
        return f"{prefijo}{self._seq}"


_store = _Store()


class MockRelationalRepository:
    async def listar_campos(self):
        return list(_store.campos.values())

    async def obtener_campo(self, campo_id):
        return _store.campos.get(campo_id)

    async def crear_campo(self, nombre, propietario_id):
        cid = _store.next_id("c")
        c = CampoDTO(cid, nombre, propietario_id)
        _store.campos[cid] = c
        return c

    async def listar_parcelas(self, campo_id=None):
        return [p for p in _store.parcelas.values()
                if campo_id is None or p.campo_id == campo_id]

    async def obtener_parcela(self, parcela_id):
        return _store.parcelas.get(parcela_id)

    async def crear_parcela(self, nombre, campo_id, cultivo_id, poligono):
        pid = _store.next_id("p")
        p = ParcelaDTO(pid, nombre, campo_id, cultivo_id, poligono)
        _store.parcelas[pid] = p
        return p

    async def listar_cultivos(self):
        return list(_store.cultivos.values())

    async def crear_cultivo(self, nombre):
        cid = _store.next_id("cu")
        c = CultivoDTO(cid, nombre)
        _store.cultivos[cid] = c
        return c


class MockTimeSeriesRepository:
    async def ultima_lectura(self, parcela_id):
        if parcela_id not in _store.parcelas:
            return None
        demo = {"p1": (42.5, 18.3), "p2": (28.1, 21.7), "p3": (55.0, 16.0)}
        humedad, temperatura = demo.get(parcela_id, (40.0, 20.0))
        return LecturaDTO(parcela_id, humedad, temperatura, _ahora())


class MockAnalyticsEngine:
    async def predicciones(self, parcela_id):
        if parcela_id not in _store.parcelas:
            return None
        return PrediccionDTO(parcela_id, "Riego recomendado en 48 h",
                             "Sin necesidad inmediata", 0.74, _ahora())

    async def reporte_campo(self, campo_id, parcela_ids):
        return ReporteDTO(campo_id,
                          f"Reporte de {len(parcela_ids)} parcela(s): condiciones estables.",
                          _ahora(), parcela_ids)
