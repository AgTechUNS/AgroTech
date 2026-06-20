from datetime import datetime, timedelta, timezone

from modules.analytics_engine.models import AlertaRecomendacion, Prediccion


def _filtrar_ventana(
    lecturas: list[dict],
    campo_telemetria: str,
    ventana_minutos: int,
) -> list[dict]:
    ahora = datetime.now(timezone.utc)
    desde = ahora - timedelta(minutes=ventana_minutos)
    filtradas: list[dict] = []
    for r in lecturas:
        ts = r.get("_time")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if ts is None or ts < desde or ts > ahora:
            continue
        if r.get("_field") != campo_telemetria:
            continue
        filtradas.append(r)
    return filtradas


def _extraer_valores(lecturas: list[dict]) -> list[float]:
    valores: list[float] = []
    for r in lecturas:
        v = r.get("_value")
        if v is not None:
            try:
                valores.append(float(v))
            except (ValueError, TypeError):
                continue
    return valores


def _calcular_promedio(valores: list[float]) -> float | None:
    if not valores:
        return None
    return sum(valores) / len(valores)


def _calcular_maximo(valores: list[float]) -> float | None:
    if not valores:
        return None
    return max(valores)


def _calcular_minimo(valores: list[float]) -> float | None:
    if not valores:
        return None
    return min(valores)


async def evaluar_umbral_humedad(
    lecturas: list[dict],
    nombreParcela: str,
    umbral: float,
    ventana_minutos: int = 60,
) -> AlertaRecomendacion | None:
    ventana = _filtrar_ventana(lecturas, "humedad", ventana_minutos)
    valores = _extraer_valores(ventana)
    promedio = _calcular_promedio(valores)
    if promedio is None:
        return None
    if promedio < umbral:
        return AlertaRecomendacion(
            tipo="ALERTA_TIEMPO_REAL",
            fechaEmision=datetime.now(timezone.utc),
            mensaje=f"Estrés hídrico detectado en {nombreParcela}: humedad promedio {promedio:.1f}% por debajo del umbral {umbral:.1f}%",
            nombreParcela=nombreParcela,
        )
    return None


async def evaluar_umbral_temperatura(
    lecturas: list[dict],
    nombreParcela: str,
    umbral: float,
    ventana_minutos: int = 60,
) -> AlertaRecomendacion | None:
    ventana = _filtrar_ventana(lecturas, "temperatura", ventana_minutos)
    valores = _extraer_valores(ventana)
    maximo = _calcular_maximo(valores)
    if maximo is None:
        return None
    if maximo > umbral:
        return AlertaRecomendacion(
            tipo="ALERTA_TIEMPO_REAL",
            fechaEmision=datetime.now(timezone.utc),
            mensaje=f"Calor extremo detectado en {nombreParcela}: temperatura máxima {maximo:.1f}°C supera el umbral {umbral:.1f}°C",
            nombreParcela=nombreParcela,
        )
    return None


def _calcular_tendencia(valores_ordenados: list[dict]) -> str:
    if len(valores_ordenados) < 2:
        return "Sin datos suficientes para estimar tendencia"
    primero = valores_ordenados[0]
    ultimo = valores_ordenados[-1]
    v1 = primero.get("_value", 0)
    v2 = ultimo.get("_value", 0)
    try:
        v1, v2 = float(v1), float(v2)
    except (ValueError, TypeError):
        return "Datos no numéricos, no se puede calcular tendencia"
    delta = v2 - v1
    if abs(delta) < 0.5:
        return "Tendencia estable esperada"
    if delta > 0:
        return f"Tendencia al alza detectada (+{delta:.1f}), se recomienda monitorear"
    return f"Tendencia a la baja detectada ({delta:.1f}), se recomienda revisar cultivo"


async def generar_prediccion(
    nombreParcela: str,
    fechaIni: datetime,
    fechaFin: datetime,
    lecturas: list[dict] | None = None,
    ndvi: float | None = None,
    temperatura_externa: float | None = None,
    humedad_externa: float | None = None,
) -> Prediccion:
    partes: list[str] = []
    if lecturas:
        tendencia = _calcular_tendencia(lecturas)
        partes.append(tendencia)
    if ndvi is not None:
        if ndvi > 0.7:
            partes.append("NDVI alto: vegetación saludable")
        elif ndvi < 0.3:
            partes.append("NDVI bajo: posible estrés vegetal")
        else:
            partes.append("NDVI dentro de rango normal")
    if temperatura_externa is not None:
        if temperatura_externa > 35:
            partes.append("alerta: calor extremo pronosticado")
        elif temperatura_externa < 0:
            partes.append("alerta: riesgo de helada")
    if humedad_externa is not None and humedad_externa < 30:
        partes.append("ambiente seco, monitorear riego")
    if not partes:
        partes.append(f"Condiciones estables esperadas para {nombreParcela}")

    partes.append(
        f"para {nombreParcela} entre {fechaIni.strftime('%d/%m')} y {fechaFin.strftime('%d/%m')}"
    )
    return Prediccion(
        fechaEmision=datetime.now(timezone.utc),
        resultado=". ".join(partes),
        fechaIni=fechaIni,
        fechaFin=fechaFin,
    )
