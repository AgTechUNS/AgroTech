"""Controller de Predicciones (CU-08). Delega en el Analytics Engine."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..dependencies import (get_analytics_engine, get_relational_repo,
                            get_security_context, verificar_acceso_parcela)
from ..ports import (AnalyticsEnginePort, RelationalRepositoryPort,
                    SecurityContext)
from ..schemas import PrediccionOut

router = APIRouter(prefix="/predicciones", tags=["Predicciones"])


@router.get("", response_model=PrediccionOut)
async def obtener_prediccion(  # CU-08
    parcela_id: str = Query(...),
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
    engine: AnalyticsEnginePort = Depends(get_analytics_engine),
):
    parcela = await repo.obtener_parcela(parcela_id)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada.")
    verificar_acceso_parcela(ctx, parcela)
    pred = await engine.predicciones(parcela_id)
    if not pred:
        raise HTTPException(404, "Sin predicción disponible.")
    return PrediccionOut(parcela_id=pred.parcela_id,
                         necesidad_riego=pred.necesidad_riego,
                         necesidad_fertilizacion=pred.necesidad_fertilizacion,
                         ndvi=pred.ndvi, generada_en=pred.generada_en)
