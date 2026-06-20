from datetime import datetime, timedelta, timezone

from infrastructure.time_series_repo.influx_client import TimeSeriesRepository
from modules.analytics_engine.engine import (
    _calcular_promedio,
    _extraer_valores,
    _filtrar_ventana,
)
from modules.analytics_engine.models import AlertaRecomendacion
from modules.iot_ingestion.query_models import TelemetryQuery


async def generar_recomendaciones_diarias(
    lecturas_historicas: list[dict],
    nombreParcela: str,
    emailUsuario: str | None = None,
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
    return recomendaciones


async def run_batch_diario(
    repo: TimeSeriesRepository,
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
        )
        todas.extend(recomendaciones)
    return todas
