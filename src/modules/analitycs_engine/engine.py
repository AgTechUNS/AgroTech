from datetime import datetime, timedelta, timezone

from modules.analitycs_engine.models import (
    MetricaAgregacion,
    NivelAlerta,
    OperadorComparacion,
    ReglaEvaluacion,
    ResultadoPrediccion,
)


def _filtrar_ventana(
    lecturas: list[dict],
    campo_telemetria: str,
    ventana_minutos: int,
) -> list[dict]:
    """Filtra lecturas dentro de la ventana temporal y que tengan el campo solicitado."""
    ahora = datetime.now(timezone.utc)
    desde = ahora - timedelta(minutes=ventana_minutos)
    filtradas = []
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
    """Extrae los valores numéricos de las lecturas filtradas."""
    valores = []
    for r in lecturas:
        v = r.get("_value")
        if v is not None:
            try:
                valores.append(float(v))
            except (ValueError, TypeError):
                continue
    return valores


def _calcular_metrica(valores: list[float], metrica: MetricaAgregacion) -> float | None:
    """Calcula la métrica agregada sobre una lista de valores."""
    if not valores:
        return None
    if metrica == "promedio":
        return sum(valores) / len(valores)
    elif metrica == "maximo":
        return max(valores)
    elif metrica == "minimo":
        return min(valores)
    return None


def _evaluar_condicion(
    valor_calculado: float,
    umbral: float,
    operador: OperadorComparacion,
) -> bool:
    """Evalúa la comparación lógica contra el umbral."""
    if operador == "<":
        return valor_calculado < umbral
    elif operador == ">":
        return valor_calculado > umbral
    elif operador == "<=":
        return valor_calculado <= umbral
    elif operador == ">=":
        return valor_calculado >= umbral
    elif operador == "==":
        return abs(valor_calculado - umbral) < 1e-9
    return False


def _clasificar_alerta(
    valor_calculado: float,
    umbral: float,
    operador: OperadorComparacion,
) -> NivelAlerta:
    """Clasifica la severidad: rojo si cumple, amarillo si está cerca, verde si no."""
    if _evaluar_condicion(valor_calculado, umbral, operador):
        return "rojo"
    margen = abs(umbral) * 0.1 if abs(umbral) > 1e-6 else 0.1
    umbral_cercano = umbral + margen if operador in (">", ">=") else umbral - margen
    if _evaluar_condicion(valor_calculado, umbral_cercano, operador):
        return "amarillo"
    return "verde"


def _generar_mensaje(
    tipo: str,
    campo_id: str,
    parcela_id: str | None,
    valor_calculado: float,
    umbral: float,
    nivel: NivelAlerta,
) -> str:
    """Genera un mensaje legible según el tipo de regla disparada."""
    base = f"{campo_id}" + (f" / {parcela_id}" if parcela_id else "")
    if nivel == "rojo":
        if tipo == "helada":
            return f"⚠️ RIESGO DE HELADA en {base}: {valor_calculado:.1f}°C (umbral {umbral:.1f}°C)"
        elif tipo == "sequia":
            return f"⚠️ RIESGO DE SEQUÍA en {base}: humedad {valor_calculado:.1f}% (umbral {umbral:.1f}%)"
        elif tipo == "calor_extremo":
            return f"⚠️ CALOR EXTREMO en {base}: {valor_calculado:.1f}°C (umbral {umbral:.1f}°C)"
        elif tipo == "anomalia_humedad":
            return f"⚠️ ANOMALÍA DE HUMEDAD en {base}: {valor_calculado:.1f}% (umbral {umbral:.1f}%)"
        return f"⚠️ ALERTA en {base}: {valor_calculado:.2f} (umbral {umbral:.2f})"
    elif nivel == "amarillo":
        return f"⚡ PRECAUCIÓN en {base}: valor {valor_calculado:.2f} cerca del umbral {umbral:.2f}"
    return f"✅ Sin novedades en {base}"


async def evaluar_regla(
    lecturas: list[dict],
    regla: ReglaEvaluacion,
) -> ResultadoPrediccion | None:
    """Evalúa una regla de umbral contra lecturas históricas de sensores.

    Args:
        lecturas: Lista de dicts devuelta por TimeSeriesRepository.query()
        regla: Definición de la regla a evaluar.

    Returns:
        ResultadoPrediccion si la condición se cumple o está cerca,
        None si todo está dentro de parámetros (verde).
    """
    if not regla.habilitada:
        return None

    # 1. Filtrar ventana temporal + campo de telemetría
    ventana = _filtrar_ventana(lecturas, regla.campo_telemetria, regla.ventana_minutos)
    if not ventana:
        return None

    # 2. Extraer valores numéricos
    valores = _extraer_valores(ventana)
    if not valores:
        return None

    # 3. Calcular métrica agregada
    valor_calculado = _calcular_metrica(valores, regla.metrica)
    if valor_calculado is None:
        return None

    # 4. Clasificar nivel de alerta
    nivel = _clasificar_alerta(valor_calculado, regla.umbral, regla.operador)
    if nivel == "verde":
        return None

    # 5. Generar mensaje
    mensaje = _generar_mensaje(
        regla.tipo,
        regla.campo_id,
        regla.parcela_id,
        valor_calculado,
        regla.umbral,
        nivel,
    )

    return ResultadoPrediccion(
        regla=regla,
        campo_id=regla.campo_id,
        parcela_id=regla.parcela_id,
        timestamp=datetime.now(timezone.utc),
        valor_calculado=valor_calculado,
        nivel_alerta=nivel,
        mensaje=mensaje,
        lecturas_consideradas=len(valores),
    )


async def evaluar_reglas(
    lecturas: list[dict],
    reglas: list[ReglaEvaluacion],
) -> list[ResultadoPrediccion]:
    """Evalúa múltiples reglas contra un mismo conjunto de lecturas.

    Returns:
        Solo las reglas que dispararon alerta (rojo o amarillo).
    """
    resultados: list[ResultadoPrediccion] = []
    for regla in reglas:
        resultado = await evaluar_regla(lecturas, regla)
        if resultado is not None:
            resultados.append(resultado)
    return resultados
