import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from infrastructure.relational_repo.repository import RelationalRepository
from modules.security.get_current_user import get_current_user
from modules.security.schemas import UserContext

from .gateway import (
    _ndmi_a_humedad_suelo,
    fetch_satellite_indices,
    fetch_weather,
    parsear_coordenadas,
)
from .models import (
    CampoNdviItem,
    SatelitalHistorialItem,
    SatelitalResponse,
    WeatherResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/external", tags=["External Data Gateway"])


def _obtener_relational_repo(request: Request) -> RelationalRepository | None:
    return getattr(request.app.state, "relational_repo", None)


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitud (-90 a 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud (-180 a 180)"),
    user: UserContext = Depends(get_current_user),
):
    return await fetch_weather(lat, lon)


@router.get("/satelital", response_model=SatelitalResponse)
async def get_satelital(
    coordenadas: str = Query(
        ..., description="GeoJSON Point o Polygon con los límites de consulta"
    ),
    nombre_parcela: str | None = Query(
        None, description="Nombre de parcela para persistir el dato"
    ),
    nombre_campo: str | None = Query(
        None, description="Nombre del campo al que pertenece la parcela"
    ),
    relational_repo: RelationalRepository | None = Depends(_obtener_relational_repo),
    user: UserContext = Depends(get_current_user),
):
    try:
        lat, lon = parsear_coordenadas(coordenadas)
    except (ValueError, json.JSONDecodeError, KeyError, IndexError):
        raise HTTPException(
            status_code=400,
            detail="GeoJSON inválido: se espera un objeto Point o Polygon con coordenadas válidas",
        )
    try:
        sat = await fetch_satellite_indices("", lat, lon)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if relational_repo is not None and nombre_parcela and nombre_campo:
        try:
            id_imagen = sat.date.strftime("GEE-%Y%m%dT%H%M%S")
            await relational_repo.create_imagen_satelital(
                id_imagen=id_imagen,
                fecha_captura=sat.date,
                proveedor=sat.source,
            )
            await relational_repo.asociar_imagen_a_parcela(
                id_imagen=id_imagen,
                nombre_parcela=nombre_parcela,
                nombre_campo=nombre_campo,
                ndvi=sat.ndvi,
                ndmi=sat.ndmi,
            )
            logger.info(
                "NDVI persistido para %s/%s: %.3f",
                nombre_campo, nombre_parcela, sat.ndvi,
            )
        except Exception:
            logger.warning("No se pudo persistir NDVI para %s/%s", nombre_campo, nombre_parcela, exc_info=True)

    return SatelitalResponse(
        ndvi=sat.ndvi,
        humedad_suelo_estimada=_ndmi_a_humedad_suelo(sat.ndmi),
    )


@router.get("/satelital/historial", response_model=list[SatelitalHistorialItem])
async def get_satelital_historial(
    nombre_parcela: str = Query(..., description="Nombre de la parcela"),
    nombre_campo: str = Query(..., description="Nombre del campo"),
    relational_repo: RelationalRepository | None = Depends(_obtener_relational_repo),
    user: UserContext = Depends(get_current_user),
):
    if relational_repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos relacional no disponible.",
        )
    registros = await relational_repo.get_imagenes_by_parcela(
        nombre_parcela=nombre_parcela,
        nombre_campo=nombre_campo,
    )
    return [
        SatelitalHistorialItem(
            id_imagen=r.id_imagen,
            fecha_captura=r.imagen.fecha_captura,
            ndvi=r.indice_ndvi,
            ndmi=r.indice_ndmi,
        )
        for r in registros
    ]


@router.get("/satelital/campo/{nombreCampo}", response_model=list[CampoNdviItem])
async def get_satelital_campo(
    nombreCampo: str,
    relational_repo: RelationalRepository | None = Depends(_obtener_relational_repo),
    user: UserContext = Depends(get_current_user),
):
    if relational_repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos relacional no disponible.",
        )
    parcelas = await relational_repo.list_parcelas_by_campo(nombreCampo)
    resultado: list[CampoNdviItem] = []
    for p in parcelas:
        registros = await relational_repo.get_imagenes_by_parcela(
            nombre_parcela=p.nombre_parcela,
            nombre_campo=nombreCampo,
            limit=1,
        )
        if registros:
            r = registros[0]
            resultado.append(
                CampoNdviItem(
                    nombre_parcela=p.nombre_parcela,
                    ndvi=r.indice_ndvi,
                    ndmi=r.indice_ndmi,
                    fecha_captura=r.imagen.fecha_captura,
                )
            )
        else:
            resultado.append(
                CampoNdviItem(nombre_parcela=p.nombre_parcela)
            )
    return resultado
