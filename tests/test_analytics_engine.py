import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "src")

from modules.analytics_engine.engine import (
    evaluar_umbral_humedad,
    evaluar_umbral_temperatura,
    generar_prediccion,
    evaluar_regla,
    evaluar_reglas,
    _filtrar_ventana,
    _extraer_valores,
    _calcular_promedio,
    _calcular_maximo,
    _calcular_minimo,
    _calcular_metrica,
    _evaluar_condicion,
    _clasificar_alerta,
    _generar_mensaje,
)
from modules.analytics_engine.models import (
    ReglaEvaluacion,
    ResultadoPrediccion,
    Prediccion,
)

ahora = datetime.now(timezone.utc)

def _lectura(ts, field, value):
    return {"_time": ts.isoformat(), "_field": field, "_value": value}

def _hacer_lecturas_humedad(
    valores: list[float],
    base: datetime | None = None,
    minutos_atras: int = 5,
) -> list[dict]:
    base = base or ahora
    return [
        _lectura(base - timedelta(minutes=i * minutos_atras), "humedad", v)
        for i, v in enumerate(valores)
    ]

def _hacer_lecturas_temperatura(
    valores: list[float],
    base: datetime | None = None,
    minutos_atras: int = 5,
) -> list[dict]:
    base = base or ahora
    return [
        _lectura(base - timedelta(minutes=i * minutos_atras), "temperatura", v)
        for i, v in enumerate(valores)
    ]

# ── Filtrado de ventana ─────────────────────────

def test_filtrar_ventana_filtra_por_campo():
    lecturas = [
        _lectura(ahora, "humedad", 50),
        _lectura(ahora, "temperatura", 30),
    ]
    result = _filtrar_ventana(lecturas, "humedad", 60)
    assert len(result) == 1
    assert result[0]["_field"] == "humedad"

def test_filtrar_ventana_excluye_fuera_de_rango():
    pasada = ahora - timedelta(minutes=120)
    lecturas = [_lectura(pasada, "humedad", 50)]
    result = _filtrar_ventana(lecturas, "humedad", 60)
    assert len(result) == 0

# ── Extracción de valores ───────────────────────

def test_extraer_valores():
    lecturas = [
        _lectura(ahora, "humedad", 10),
        _lectura(ahora, "humedad", 20),
        _lectura(ahora, "humedad", 30),
    ]
    assert _extraer_valores(lecturas) == [10.0, 20.0, 30.0]

def test_extraer_valores_ignora_none():
    lecturas = [{"_value": None}, {"_value": 5}]
    assert _extraer_valores(lecturas) == [5.0]

# ── Cálculos ────────────────────────────────────

def test_calcular_promedio():
    assert _calcular_promedio([10, 20, 30]) == 20.0

def test_calcular_promedio_vacio():
    assert _calcular_promedio([]) is None

def test_calcular_maximo():
    assert _calcular_maximo([10, 50, 30]) == 50.0

def test_calcular_minimo():
    assert _calcular_minimo([10, 50, 30]) == 10.0

def test_calcular_metrica_promedio():
    assert _calcular_metrica([10, 20, 30], "promedio") == 20.0

def test_calcular_metrica_maximo():
    assert _calcular_metrica([10, 50, 30], "maximo") == 50.0

def test_calcular_metrica_minimo():
    assert _calcular_metrica([50, 10, 30], "minimo") == 10.0

def test_calcular_metrica_vacio():
    assert _calcular_metrica([], "promedio") is None

# ── Evaluación de condiciones ───────────────────

def test_evaluar_condicion_menor():
    assert _evaluar_condicion(5, 10, "<") is True
    assert _evaluar_condicion(10, 10, "<") is False

def test_evaluar_condicion_mayor():
    assert _evaluar_condicion(15, 10, ">") is True
    assert _evaluar_condicion(10, 10, ">") is False

def test_evaluar_condicion_igual():
    assert _evaluar_condicion(10, 10, "==") is True
    assert _evaluar_condicion(11, 10, "==") is False

# ── Clasificación de alertas ────────────────────

def test_clasificar_alerta_rojo():
    assert _clasificar_alerta(5, 10, "<") == "rojo"

def test_clasificar_alerta_amarillo():
    # Para ">" con umbral 38: rojo es > 38, amarillo es > 34.2 (38 - 3.8)
    assert _clasificar_alerta(36, 38, ">") == "amarillo"

def test_clasificar_alerta_verde():
    assert _clasificar_alerta(50, 10, "<") == "verde"

# ── Mensajes ────────────────────────────────────

def test_generar_mensaje_rojo_helada():
    msg = _generar_mensaje("helada", "Campo1", "Parcela1", -2, 0, "rojo")
    assert "RIESGO DE HELADA" in msg

def test_generar_mensaje_amarillo():
    msg = _generar_mensaje("sequia", "Campo1", None, 15, 20, "amarillo")
    assert "PRECAUCIÓN" in msg

def test_generar_mensaje_verde():
    msg = _generar_mensaje("sequia", "Campo1", None, 50, 20, "verde")
    assert "Sin novedades" in msg

# ── Evaluar umbral humedad (asíncrono) ──────────

async def test_evaluar_umbral_humedad_dispara_alerta():
    lecturas = _hacer_lecturas_humedad([10, 12, 8])
    result = await evaluar_umbral_humedad(lecturas, "ParcelaTest", 20.0, 60)
    assert result is not None
    assert result.alerta.nombreParcela == "ParcelaTest"
    assert "Estrés hídrico" in result.alerta.mensaje
    assert result.valor_calculado == 10.0
    assert result.umbral == 20.0

async def test_evaluar_umbral_humedad_normal():
    lecturas = _hacer_lecturas_humedad([50, 60, 55])
    result = await evaluar_umbral_humedad(lecturas, "ParcelaTest", 20.0, 60)
    assert result is None

async def test_evaluar_umbral_humedad_sin_datos():
    result = await evaluar_umbral_humedad([], "ParcelaTest", 20.0, 60)
    assert result is None

# ── Evaluar umbral temperatura ──────────────────

async def test_evaluar_umbral_temperatura_dispara_alerta():
    lecturas = _hacer_lecturas_temperatura([40, 42, 39])
    result = await evaluar_umbral_temperatura(lecturas, "ParcelaTest", 38.0, 60)
    assert result is not None
    assert "Calor extremo" in result.alerta.mensaje
    assert result.valor_calculado == 42.0

async def test_evaluar_umbral_temperatura_normal():
    lecturas = _hacer_lecturas_temperatura([25, 26, 24])
    result = await evaluar_umbral_temperatura(lecturas, "ParcelaTest", 38.0, 60)
    assert result is None

async def test_evaluar_umbral_temperatura_sin_datos():
    result = await evaluar_umbral_temperatura([], "ParcelaTest", 38.0, 60)
    assert result is None

# ── Generar predicción ──────────────────────────

async def test_generar_prediccion_con_lecturas():
    lecturas = _hacer_lecturas_humedad([30, 35, 32], minutos_atras=1)
    pred = await generar_prediccion(
        nombreParcela="ParcelaTest",
        fechaIni=ahora,
        fechaFin=ahora + timedelta(days=3),
        lecturas=lecturas,
    )
    assert isinstance(pred, Prediccion)
    assert "ParcelaTest" in pred.resultado

async def test_generar_prediccion_con_ndvi_alto():
    pred = await generar_prediccion(
        nombreParcela="Test", fechaIni=ahora, fechaFin=ahora, ndvi=0.8,
    )
    assert "NDVI alto" in pred.resultado

async def test_generar_prediccion_con_ndvi_bajo():
    pred = await generar_prediccion(
        nombreParcela="Test", fechaIni=ahora, fechaFin=ahora, ndvi=0.2,
    )
    assert "NDVI bajo" in pred.resultado

async def test_generar_prediccion_calor_extremo():
    pred = await generar_prediccion(
        nombreParcela="Test", fechaIni=ahora, fechaFin=ahora, temperatura_externa=40,
    )
    assert "calor extremo" in pred.resultado

async def test_generar_prediccion_helada():
    pred = await generar_prediccion(
        nombreParcela="Test", fechaIni=ahora, fechaFin=ahora, temperatura_externa=-2,
    )
    assert "helada" in pred.resultado

async def test_generar_prediccion_sin_datos():
    pred = await generar_prediccion("Test", ahora, ahora)
    assert "Condiciones estables" in pred.resultado

# ── Motor de reglas configurable ────────────────

async def test_evaluar_regla_dispara_alerta():
    regla = ReglaEvaluacion(
        tipo="sequia",
        campo_id="Campo1",
        parcela_id="Parcela1",
        umbral=20.0,
        ventana_minutos=60,
        operador="<",
        metrica="promedio",
        campo_telemetria="humedad",
    )
    lecturas = _hacer_lecturas_humedad([10, 12, 8])
    result = await evaluar_regla(lecturas, regla)
    assert result is not None
    assert result.nivel_alerta == "rojo"
    assert "SEQUÍA" in result.mensaje

async def test_evaluar_regla_deshabilitada():
    regla = ReglaEvaluacion(
        tipo="sequia", campo_id="C1", umbral=20, habilitada=False,
    )
    lecturas = _hacer_lecturas_humedad([10, 12, 8])
    result = await evaluar_regla(lecturas, regla)
    assert result is None

async def test_evaluar_regla_sin_lecturas():
    regla = ReglaEvaluacion(tipo="sequia", campo_id="C1", umbral=20)
    result = await evaluar_regla([], regla)
    assert result is None

async def test_evaluar_reglas_varias():
    regla1 = ReglaEvaluacion(
        tipo="sequia", campo_id="C1", umbral=20, campo_telemetria="humedad",
    )
    regla2 = ReglaEvaluacion(
        tipo="calor_extremo", campo_id="C1", umbral=30, operador=">", campo_telemetria="temperatura",
    )
    lecturas = _hacer_lecturas_humedad([10]) + _hacer_lecturas_temperatura([40])
    results = await evaluar_reglas(lecturas, [regla1, regla2])
    assert len(results) == 2

async def test_evaluar_reglas_sin_coincidencias():
    regla = ReglaEvaluacion(
        tipo="sequia", campo_id="C1", umbral=10, campo_telemetria="humedad",
    )
    lecturas = _hacer_lecturas_humedad([50, 60])
    results = await evaluar_reglas(lecturas, [regla])
    assert len(results) == 0
