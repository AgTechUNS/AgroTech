"""Controller de Reportes (CU-06). Delega en el Analytics Engine."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..dependencies import (get_analytics_engine, get_relational_repo,
                            get_security_context, verificar_acceso_campo)
from ..ports import (AnalyticsEnginePort, RelationalRepositoryPort,
                    SecurityContext)
from ..schemas import ReporteOut

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("", response_model=ReporteOut)
async def reporte_campo(  # CU-06
    campo_id: str = Query(...),
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
    engine: AnalyticsEnginePort = Depends(get_analytics_engine),
):
    campo = await repo.obtener_campo(campo_id)
    if not campo:
        raise HTTPException(404, "Campo no encontrado.")
    verificar_acceso_campo(ctx, campo_id)
    parcelas = await repo.listar_parcelas(campo_id)
    rep = await engine.reporte_campo(campo_id, [p.id for p in parcelas])
    return ReporteOut(campo_id=rep.campo_id, resumen=rep.resumen,
                      generado_en=rep.generado_en, parcelas=rep.parcelas)
