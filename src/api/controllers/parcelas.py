"""Controller de Parcelas. Cubre CU-01 (estado) y CU-03 (alta con polígono válido)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..dependencies import (get_relational_repo, get_security_context,
                            get_timeseries_repo, verificar_acceso_campo,
                            verificar_acceso_parcela)
from ..ports import (RelationalRepositoryPort, SecurityContext,
                    TimeSeriesRepositoryPort)
from ..schemas import EstadoParcelaOut, LecturaOut, ParcelaCreate, ParcelaOut

router = APIRouter(prefix="/parcelas", tags=["Parcelas"])


@router.get("", response_model=list[ParcelaOut])
async def listar_parcelas(
    campo_id: str | None = Query(default=None),
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    parcelas = await repo.listar_parcelas(campo_id)
    if ctx.es_admin:
        return parcelas
    return [p for p in parcelas if p.campo_id in ctx.campos_asignados]


@router.post("", response_model=ParcelaOut, status_code=201)
async def crear_parcela(  # CU-03 (la validez del polígono la garantiza ParcelaCreate)
    payload: ParcelaCreate,
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    campo = await repo.obtener_campo(payload.campo_id)
    if not campo:
        raise HTTPException(404, "Campo destino no encontrado.")
    verificar_acceso_campo(ctx, payload.campo_id)
    return await repo.crear_parcela(payload.nombre, payload.campo_id,
                                    payload.cultivo_id, payload.poligono)


@router.get("/{parcela_id}", response_model=ParcelaOut)
async def obtener_parcela(
    parcela_id: str,
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    parcela = await repo.obtener_parcela(parcela_id)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada.")
    verificar_acceso_parcela(ctx, parcela)
    return parcela


@router.get("/{parcela_id}/estado", response_model=EstadoParcelaOut)
async def estado_parcela(  # CU-01: combina Relational + Time Series
    parcela_id: str,
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
    ts: TimeSeriesRepositoryPort = Depends(get_timeseries_repo),
):
    parcela = await repo.obtener_parcela(parcela_id)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada.")
    verificar_acceso_parcela(ctx, parcela)
    lectura = await ts.ultima_lectura(parcela_id)
    lectura_out = None
    alerta = None
    if lectura:
        lectura_out = LecturaOut(humedad=lectura.humedad,
                                 temperatura=lectura.temperatura,
                                 timestamp=lectura.timestamp)
        if lectura.humedad < 30:
            alerta = "Humedad baja: posible estrés hídrico."
    return EstadoParcelaOut(parcela_id=parcela_id, nombre=parcela.nombre,
                            ultima_lectura=lectura_out, alerta=alerta)
