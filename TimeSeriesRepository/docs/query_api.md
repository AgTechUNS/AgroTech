# API de Consultas — TimeSeriesRepository

## Métodos de consulta

### `query(spec: TelemetryQuery) -> list[dict]`
Construye y ejecuta una consulta Flux a partir del objeto `TelemetryQuery`.

### `query_raw(flux_query: str) -> list[dict]`
Ejecuta una consulta Flux directamente (escape hatch para consultas no cubiertas por `TelemetryQuery`).

Ambos métodos retornan `list[dict]`, donde cada dict corresponde a un registro de la base de datos con todas sus columnas.

---

## TelemetryQuery — Campos

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `sensors` | `list[str] \| None` | `None` | Filtrar por ID de sensor(es) |
| `campos` | `list[str] \| None` | `None` | Filtrar por ID de campo(s) |
| `parcelas` | `list[str] \| None` | `None` | Filtrar por ID de parcela(s) |
| `fields` | `list[str] \| None` | `None` | Filtrar por campo(s) de telemetría (`temperatura`, `humedad`) |
| `time_from` | `datetime \| None` | `None` | Inicio de ventana temporal (default: 7 días atrás) |
| `time_to` | `datetime \| None` | `None` | Fin de ventana temporal (default: ahora) |
| `aggregate_window` | `str \| None` | `None` | Ventana de agregación (ej. `"1h"`, `"1d"`, `"30m"`) |
| `aggregate_function` | `str \| None` | `None` | Función de agregación: `mean`, `max`, `min`, `last`, `first`, `count`, `sum` |
| `group_by` | `list[str] \| None` | `None` | Columnas para reagrupar antes de agregar (ej. `["campo_id"]`). Lista vacía fusiona todos los grupos |
| `pivot` | `bool` | `False` | Si `True`, convierte `_field`/`_value` en columnas separadas |
| `limit` | `int \| None` | `None` | Máximo de registros a retornar |
| `order` | `"asc" \| "desc"` | `"desc"` | Orden temporal |

---

## Ejemplos de consultas

### 1. Últimas lecturas crudas de un sensor

```python
from datetime import datetime, timedelta
from IngestionIoT.query_models import TelemetryQuery

resultado = await repo.query(TelemetryQuery(
    sensors=["sensor-0"],
    fields=["temperatura", "humedad"],
    limit=10,
))
```

**Output** (sin pivot):
```json
[
  {"_time": "2026-06-06T12:00:00Z", "_field": "temperatura", "_value": 24.5, "id_sensor": "sensor-0", "campo_id": "campo-0", "id_parcela": "parcela-0"},
  {"_time": "2026-06-06T12:00:00Z", "_field": "humedad", "_value": 65.0, "id_sensor": "sensor-0", "campo_id": "campo-0", "id_parcela": "parcela-0"},
  ...
]
```

### 2. Últimas lecturas con pivot (campos como columnas)

```python
resultado = await repo.query(TelemetryQuery(
    sensors=["sensor-0"],
    fields=["temperatura", "humedad"],
    pivot=True,
    limit=10,
))
```

**Output** (con pivot):
```json
[
  {"_time": "2026-06-06T12:00:00Z", "temperatura": 24.5, "humedad": 65.0, "id_sensor": "sensor-0", "campo_id": "campo-0", "id_parcela": "parcela-0"},
  ...
]
```

### 3. Lecturas de un campo completo en una ventana temporal

```python
resultado = await repo.query(TelemetryQuery(
    campos=["campo-0"],
    fields=["temperatura"],
    time_from=datetime.utcnow() - timedelta(hours=6),
    pivot=True,
    order="asc",
))
```

### 4. Promedio diario de temperatura y humedad por campo (última semana)

```python
resultado = await repo.query(TelemetryQuery(
    fields=["temperatura", "humedad"],
    aggregate_window="1d",
    aggregate_function="mean",
    group_by=["campo_id"],
    pivot=True,
    time_from=datetime.utcnow() - timedelta(days=7),
))
```

**Output**:
```json
[
  {"_time": "2026-05-31T00:00:00Z", "temperatura": 22.1, "humedad": 58.3, "campo_id": "campo-0"},
  {"_time": "2026-05-31T00:00:00Z", "temperatura": 24.7, "humedad": 62.1, "campo_id": "campo-1"},
  {"_time": "2026-06-01T00:00:00Z", "temperatura": 23.4, "humedad": 55.8, "campo_id": "campo-0"},
  ...
]
```

### 5. Máximo de temperatura por parcela en las últimas 24 horas

```python
resultado = await repo.query(TelemetryQuery(
    fields=["temperatura"],
    aggregate_window="24h",
    aggregate_function="max",
    group_by=["id_parcela"],
    pivot=True,
    time_from=datetime.utcnow() - timedelta(hours=24),
))
```

### 6. Conteo de lecturas por sensor en la última hora

```python
resultado = await repo.query(TelemetryQuery(
    aggregate_window="1h",
    aggregate_function="count",
    group_by=["id_sensor"],
    pivot=True,
    time_from=datetime.utcnow() - timedelta(hours=1),
))
```

### 7. Consulta ad-hoc con Flux directo

```python
resultado = await repo.query_raw('''
    from(bucket: "datos_sensores")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "telemetria_sensor")
        |> filter(fn: (r) => r.campo_id == "campo-0")
        |> aggregateWindow(every: 1d, fn: mean)
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> keep(columns: ["_time", "temperatura", "humedad"])
''')
```

---

## Estructura del output

Los dicts retornados contienen las columnas que devuelve InfluxDB según la consulta:

### Sin pivot (formato serie temporal)
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `_time` | `datetime` | Timestamp de la lectura |
| `_field` | `str` | Nombre del field (`temperatura`, `humedad`) |
| `_value` | `float` | Valor numérico |
| `_measurement` | `str` | Siempre `telemetria_sensor` |
| `id_sensor` | `str` | ID del sensor (tag) |
| `campo_id` | `str` | ID del campo (tag) |
| `id_parcela` | `str` | ID de la parcela (tag) |
| `_start` | `datetime` | Inicio del rango consultado |
| `_stop` | `datetime` | Fin del rango consultado |

### Con pivot (`pivot=True`)
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `_time` | `datetime` | Timestamp de la lectura |
| `temperatura` | `float \| None` | Temperatura (si se solicitó) |
| `humedad` | `float \| None` | Humedad (si se solicitó) |
| `id_sensor` | `str` | ID del sensor |
| `campo_id` | `str` | ID del campo |
| `id_parcela` | `str` | ID de la parcela |

### Con agregación y pivot
Ídem anterior, pero `_time` corresponde al inicio de cada ventana de agregación.

---

## Notas

- Si `time_from` no se especifica, default: **7 días atrás**
- Si `time_to` no se especifica, default: **ahora**
- `aggregate_window` y `aggregate_function` deben usarse juntos
- `group_by` actúa **antes** de `aggregateWindow`, redefiniendo la clave de grupo
- Si `group_by = []` (lista vacía), todos los grupos se fusionan en uno solo
- Para obtener todos los sensores/campos/parcelas, simplemente no especifiques el filtro correspondiente
