import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from infrastructure.relational_repo.repository import RelationalRepository
from infrastructure.time_series_repo.influx_client import TimeSeriesRepository
from modules.analytics_engine.engine import (
    evaluar_umbral_humedad,
    evaluar_umbral_temperatura,
    generar_prediccion,
)
from modules.analytics_engine.models import (
    AlertaRecomendacion,
    LecturaOut,
    LecturasResponse,
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
from modules.notification_component import notify, NotificationJob
from modules.security.get_current_user import get_current_user
from modules.security.schemas import UserContext

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


def _obtener_relational_repo(request: Request) -> RelationalRepository | None:
    return getattr(request.app.state, "relational_repo", None)


def _verificar_relational_repo(repo: RelationalRepository | None) -> RelationalRepository:
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos relacional no disponible. Intente más tarde.",
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
    nombre_regla_humedad: str | None = Query(
        None, description="Nombre de regla en DB para umbral de humedad (sobrescribe umbral_humedad)"
    ),
    nombre_regla_temperatura: str | None = Query(
        None, description="Nombre de regla en DB para umbral de temperatura (sobrescribe umbral_temperatura)"
    ),
    ventana_minutos: int = Query(
        60, ge=1, le=1440, description="Ventana de tiempo en minutos"
    ),
    modo: str = Query("tiempo_real", description="Modo de consulta: 'tiempo_real' o 'historico'"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Elementos por página"),
    repo: TimeSeriesRepository | None = Depends(_obtener_repo),
    relational_repo: RelationalRepository | None = Depends(_obtener_relational_repo),
    user: UserContext = Depends(get_current_user),
):
    if modo == "historico":
        if relational_repo is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Base de datos relacional no disponible para modo histórico.",
            )
        alertas_db, total = await relational_repo.list_alertas_by_parcela(
            nombreParcela, page=page, limit=limit
        )
        data = [
            AlertaRecomendacion(
                tipo="RECOMENDACION_BATCH",
                mensaje=a.mensaje,
                fechaEmision=a.fecha_emision,
                nombreParcela=a.nombre_parcela,
            )
            for a in alertas_db
        ]
        total_pages = max(1, (total + limit - 1) // limit)
        return RecomendacionesResponse(
            data=data,
            pagination=Paginacion(
                page=page,
                limit=limit,
                total=total,
                totalPages=total_pages,
            ),
        )

    repo = _verificar_repo(repo)
    if relational_repo is not None:
        if nombre_regla_humedad is not None:
            regla_humedad = await relational_repo.get_regla_by_nombre_and_campo(
                nombre_regla_humedad, nombreCampo
            )
            if regla_humedad is not None:
                umbral_humedad = regla_humedad.valor
                logger.info(
                    "Umbral humedad desde regla '%s': %.1f", nombre_regla_humedad, umbral_humedad
                )
        if nombre_regla_temperatura is not None:
            regla_temperatura = await relational_repo.get_regla_by_nombre_and_campo(
                nombre_regla_temperatura, nombreCampo
            )
            if regla_temperatura is not None:
                umbral_temperatura = regla_temperatura.valor
                logger.info(
                    "Umbral temperatura desde regla '%s': %.1f", nombre_regla_temperatura, umbral_temperatura
                )

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
        alertas.append(resultado_humedad.alerta)
        try:
            await notify(NotificationJob(
                event_type=resultado_humedad.event_type,
                field_id=f"{nombreCampo}/{nombreParcela}",
                value=resultado_humedad.valor_calculado,
                threshold=resultado_humedad.umbral,
            ))
        except Exception:
            logger.warning("Notificación no enviada (humedad): %s", resultado_humedad.alerta.mensaje, exc_info=True)
        if relational_repo is not None:
            try:
                await relational_repo.create_alerta(
                    fecha_emision=resultado_humedad.alerta.fechaEmision,
                    mensaje=resultado_humedad.alerta.mensaje,
                    nombre_parcela=nombreParcela,
                )
            except Exception:
                logger.warning("Alerta no persistida (humedad): %s", resultado_humedad.alerta.mensaje, exc_info=True)
    resultado_temperatura = await evaluar_umbral_temperatura(
        lecturas, nombreParcela, umbral_temperatura, ventana_minutos
    )
    if resultado_temperatura:
        alertas.append(resultado_temperatura.alerta)
        try:
            await notify(NotificationJob(
                event_type=resultado_temperatura.event_type,
                field_id=f"{nombreCampo}/{nombreParcela}",
                value=resultado_temperatura.valor_calculado,
                threshold=resultado_temperatura.umbral,
            ))
        except Exception:
            logger.warning("Notificación no enviada (temperatura): %s", resultado_temperatura.alerta.mensaje, exc_info=True)
        if relational_repo is not None:
            try:
                await relational_repo.create_alerta(
                    fecha_emision=resultado_temperatura.alerta.fechaEmision,
                    mensaje=resultado_temperatura.alerta.mensaje,
                    nombre_parcela=nombreParcela,
                )
            except Exception:
                logger.warning("Alerta no persistida (temperatura): %s", resultado_temperatura.alerta.mensaje, exc_info=True)

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
    relational_repo: RelationalRepository | None = Depends(_obtener_relational_repo),
    user: UserContext = Depends(get_current_user),
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
    if relational_repo is not None:
        try:
            await relational_repo.create_prediccion(
                fecha_emision=prediccion.fechaEmision,
                resultado=prediccion.resultado,
                fecha_ini=prediccion.fechaIni,
                fecha_fin=prediccion.fechaFin,
                nombre_campo=nombreCampo,
            )
        except Exception:
            logger.warning("Prediccion no persistida para %s/%s", nombreCampo, nombreParcela, exc_info=True)
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


@router.get(
    "/{nombreCampo}/parcelas/{nombreParcela}/lecturas",
    response_model=LecturasResponse,
)
async def consultar_lecturas(
    nombreCampo: str,
    nombreParcela: str,
    minutos: int = Query(60, ge=1, le=1440),
    repo: TimeSeriesRepository | None = Depends(_obtener_repo),
    user: UserContext = Depends(get_current_user),
):
    _verificar_repo(repo)
    query = TelemetryQuery(
        campos=[nombreCampo],
        parcelas=[nombreParcela],
        time_from=datetime.now(timezone.utc) - timedelta(minutes=minutos),
        pivot=True,
        order="desc",
        limit=100,
    )
    lecturas = await repo.query(query)
    return LecturasResponse(
        data=[
            LecturaOut(
                sensorId=r.get("id_sensor", ""),
                timestamp=r.get("_time", ""),
                temperatura=r.get("temperatura"),
                humedad=r.get("humedad"),
                campoId=r.get("campo_id", ""),
                parcelaId=r.get("id_parcela", ""),
            )
            for r in lecturas
        ]
    )


# ──────────────────────────────────────────────
# CRUD de reglas migrado a /api/reglas via data_api.router
# ──────────────────────────────────────────────
