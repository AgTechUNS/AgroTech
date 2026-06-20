import logging
from datetime import datetime, timedelta, timezone

from infrastructure.relational_repo.repository import RelationalRepository
from infrastructure.time_series_repo.influx_client import TimeSeriesRepository
from modules.analytics_engine.engine import (
    _calcular_promedio,
    _extraer_valores,
    _filtrar_ventana,
)
from modules.analytics_engine.models import AlertaRecomendacion
from modules.iot_ingestion.query_models import TelemetryQuery
from modules.notification_component import EventType, notify, NotificationJob


async def generar_recomendaciones_diarias(
    lecturas_historicas: list[dict],
    nombreParcela: str,
    nombreCampo: str | None = None,
    emailUsuario: str | None = None,
    relational_repo: RelationalRepository | None = None,
) -> list[AlertaRecomendacion]:
    recomendaciones: list[AlertaRecomendacion] = []
    metricas = [
        ("humedad", 20.0, "bajo"),
        ("temperatura", 38.0, "alto"),
    ]
    for campo, umbral, direccion in metricas:
        ventana = _filtrar_ventana(lecturas_historicas, campo, 1440)
        valores = _extraer_valores(ventana)
        promedio = _calcular_promedio(valores)
        if promedio is None:
            continue
        if (direccion == "bajo" and promedio < umbral) or (
            direccion == "alto" and promedio > umbral
        ):
            recomendaciones.append(
                AlertaRecomendacion(
                    tipo="RECOMENDACION_BATCH",
                    fechaEmision=datetime.now(timezone.utc),
                    mensaje=f"Recomendación diaria para {nombreParcela}: {campo} promedio {promedio:.1f} (umbral {umbral:.1f})",
                    nombreParcela=nombreParcela,
                    emailUsuario=emailUsuario,
                )
            )
            event_type = EventType.HYDRIC_STRESS if direccion == "bajo" else EventType.HEAT_STRESS
            field_id = f"{nombreCampo}/{nombreParcela}" if nombreCampo else nombreParcela
            try:
                await notify(NotificationJob(
                    event_type=event_type,
                    field_id=field_id,
                    value=promedio,
                    threshold=umbral,
                ))
            except Exception:
                logging.getLogger(__name__).warning("Notificación batch no enviada para %s: %s", nombreParcela, campo, exc_info=True)
            if relational_repo is not None:
                try:
                    await relational_repo.create_alerta(
                        fecha_emision=datetime.now(timezone.utc),
                        mensaje=f"Recomendación diaria para {nombreParcela}: {campo} promedio {promedio:.1f} (umbral {umbral:.1f})",
                        nombre_parcela=nombreParcela,
                        email_usuario=emailUsuario,
                    )
                except Exception:
                    logging.getLogger(__name__).warning("Alerta batch no persistida para %s: %s", nombreParcela, campo, exc_info=True)
    return recomendaciones


async def run_batch_diario(
    repo: TimeSeriesRepository,
    relational_repo: RelationalRepository | None = None,
) -> list[AlertaRecomendacion]:
    ahora = datetime.now(timezone.utc)
    query = TelemetryQuery(
        time_from=ahora - timedelta(days=1),
    )
    lecturas = await repo.query(query)

    grupos: dict[tuple[str, str], list[dict]] = {}
    for r in lecturas:
        campo = r.get("campo_id")
        parcela = r.get("id_parcela")
        if not campo or not parcela:
            continue
        key = (campo, parcela)
        if key not in grupos:
            grupos[key] = []
        grupos[key].append(r)

    todas: list[AlertaRecomendacion] = []
    for (campo, parcela), lecturas_grupo in grupos.items():
        recomendaciones = await generar_recomendaciones_diarias(
            lecturas_historicas=lecturas_grupo,
            nombreParcela=parcela,
            nombreCampo=campo,
            relational_repo=relational_repo,
        )
        todas.extend(recomendaciones)
    return todas
