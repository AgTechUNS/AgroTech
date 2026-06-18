import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from infrastructure.time_series_repo.influx_client import TimeSeriesRepository
from modules.analytics_engine.engine import (
    evaluar_umbral_humedad,
    evaluar_umbral_temperatura,
    generar_prediccion,
)
from modules.analytics_engine.models import (
    AlertaRecomendacion,
    Paginacion,
    Prediccion,
    PrediccionesResponse,
    RecomendacionesResponse,
)
from modules.external_data_gateway.gateway import (
    fetch_satellite_indices,
    fetch_weather,
)
from modules.iot_ingestion.query_models import TelemetryQuery

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/campos", tags=["Analítica"])


def _obtener_repo(request: Request) -> TimeSeriesRepository | None:
    return getattr(request.app.state, "time_series_repo", None)


def _verificar_repo(repo: TimeSeriesRepository | None) -> TimeSeriesRepository:
    if repo is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos temporal no disponible. Intente más tarde.",
        )
    return repo


@router.get(
    "/{nombreCampo}/parcelas/{nombreParcela}/recomendaciones",
    response_model=RecomendacionesResponse,
)
async def consultar_recomendaciones(
    nombreCampo: str,
    nombreParcela: str,
    umbral_humedad: float = Query(20.0, description="Umbral mínimo de humedad (%)"),
    umbral_temperatura: float = Query(
        38.0, description="Umbral máximo de temperatura (°C)"
    ),
    ventana_minutos: int = Query(
        60, ge=1, le=1440, description="Ventana de tiempo en minutos"
    ),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Elementos por página"),
    repo: TimeSeriesRepository | None = Depends(_obtener_repo),
):
    repo = _verificar_repo(repo)
    query = TelemetryQuery(
        campos=[nombreCampo],
        parcelas=[nombreParcela],
        time_from=datetime.now(timezone.utc) - timedelta(minutes=ventana_minutos),
    )
    lecturas = await repo.query(query)

    alertas: list[AlertaRecomendacion] = []
    resultado_humedad = await evaluar_umbral_humedad(
        lecturas, nombreParcela, umbral_humedad, ventana_minutos
    )
    if resultado_humedad:
        alertas.append(resultado_humedad)
    resultado_temperatura = await evaluar_umbral_temperatura(
        lecturas, nombreParcela, umbral_temperatura, ventana_minutos
    )
    if resultado_temperatura:
        alertas.append(resultado_temperatura)

    total = len(alertas)
    total_pages = max(1, (total + limit - 1) // limit)
    inicio = (page - 1) * limit
    data = alertas[inicio : inicio + limit]

    return RecomendacionesResponse(
        data=data,
        pagination=Paginacion(
            page=page,
            limit=limit,
            total=total,
            totalPages=total_pages,
        ),
    )


@router.get(
    "/{nombreCampo}/parcelas/{nombreParcela}/predicciones",
    response_model=PrediccionesResponse,
)
async def consultar_predicciones(
    nombreCampo: str,
    nombreParcela: str,
    dias: int = Query(3, ge=1, le=30, description="Cantidad de días a pronosticar"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lat: float | None = Query(
        None, ge=-90, le=90, description="Latitud para enriquecer con datos externos"
    ),
    lon: float | None = Query(
        None,
        ge=-180,
        le=180,
        description="Longitud para enriquecer con datos externos",
    ),
    repo: TimeSeriesRepository | None = Depends(_obtener_repo),
):
    repo = _verificar_repo(repo)
    ahora = datetime.now(timezone.utc)
    query = TelemetryQuery(
        campos=[nombreCampo],
        parcelas=[nombreParcela],
        time_from=ahora - timedelta(days=7),
        order="asc",
    )
    lecturas = await repo.query(query)

    ndvi: float | None = None
    temperatura_externa: float | None = None
    humedad_externa: float | None = None
    if lat is not None and lon is not None:
        try:
            weather = await fetch_weather(lat, lon)
            temperatura_externa = weather.temperature_celsius
            humedad_externa = weather.humidity_percent
            sat = await fetch_satellite_indices("", lat, lon)
            ndvi = sat.ndvi
        except Exception:
            logger.warning(
                "Gateway externo no disponible para %s,%s", lat, lon, exc_info=True
            )

    prediccion = await generar_prediccion(
        nombreParcela=nombreParcela,
        fechaIni=ahora,
        fechaFin=ahora + timedelta(days=dias),
        lecturas=lecturas,
        ndvi=ndvi,
        temperatura_externa=temperatura_externa,
        humedad_externa=humedad_externa,
    )
    data = [prediccion]
    return PrediccionesResponse(
        data=data,
        pagination=Paginacion(
            page=1,
            limit=limit,
            total=len(data),
            totalPages=1,
        ),
    )
