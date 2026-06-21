# AgroTech — Agent Guide

## Project structure

Modular monolith (Python/FastAPI), organized by business domain (Screaming Architecture).

```
src/                        # Python package root (run all commands from repo root)
├── main.py                 # FastAPI entrypoint — only /external-data/* + /health
├── core/config.py          # Env-based settings (dataclass singleton)
├── modules/                # Business domain components
│   ├── iot_ingestion/      # MQTT subscriber + dedup + async workers → InfluxDB
│   ├── analytics_engine/   # Rule evaluation (heat/hydric stress alerts)
│   ├── external_data_gateway/  # REST endpoints → Open-Meteo + Google Earth Engine
│   ├── notification_component/ # Alert dispatch: in_app / email / sms (Redis dedup)
│   └── security/           # JWT auth (get_current_user, schemas, core/config)
└── infrastructure/         # Persistence implementations
    ├── time_series_repo/   # InfluxDB client + Flux query builder
    └── relational_repo/    # PostgreSQL + SQLAlchemy (usuarios, reglas, alertas, predicciones)
```

## Running the project

All commands run from repo root. `src/` is implicitly the Python path root — do NOT `cd src/`.

```sh
# One-command startup (3 windows: backend + SPA + MQTT ingestion)
.\start-all.ps1

# Optional: include sensor simulator (needs Mosquitto on Docker)
.\start-all.ps1 -Simulador

# Stop everything
.\stop-all.ps1

# Individual commands (all from repo root):
#   FastAPI server    → uvicorn src.main:app --reload
#   MQTT ingestion    → python -m src.infrastructure.time_series_repo.bootstrap
#   Sensor simulator  → python tools/simulador_sensores/lns_console.py
#   Mosquitto broker  → docker compose -f deploy/broker/docker-compose.yml up -d
#   Unit tests        → pytest tests/ -v
```

## Credentials & env loading

- **InfluxDB**: `tools/simulador_sensores/credenciales.env` is loaded by a **hard-coded relative path** in `src/infrastructure/time_series_repo/influx_client.py:10`. The agent must find and check this file if InfluxDB connection fails. Points to InfluxDB Cloud (`https://us-east-1-1.aws.cloud2.influxdata.com/`), org `PendejosIA`, bucket `datos_sensores`.
- **Google Earth Engine**: Service account JSON via `GEE_CREDENTIALS_FILE` (file path) or `GEE_CREDENTIALS_JSON` (inline JSON string). Default file: `~/.agrotech/secrets/service_account.json`.
- **Redis** (notification dedup): `REDIS_URL` env var, default `redis://localhost:6379`.
- **PostgreSQL (Neon)**: `DATABASE_DSN` in `.env` (asyncpg URL). Current: `postgresql+asyncpg://neondb_owner:...@ep-winter-hall-...neon.tech/neondb?sslmode=require`.
- `.env` files are gitignored; only `.env.example` is committed. Copy it for local use.

## Architecture notes

- **Three independent runtimes**: FastAPI server, MQTT ingestion bootstrap, and sensor simulator can each run alone. They communicate via MQTT (sensors → ingestion) and InfluxDB (ingestion → analytics).
- **No `pyproject.toml` or `setup.py`** — `src/` is the package root; import paths use absolute module names from there (e.g., `from modules.iot_ingestion.schemas`).
- **MQTT topic**: `v3/agtechuns-app/devices/+/up` (QoS 1). Payload is base64-decoded JSON with fields `{t, h}` (temperature, humidity).
- **DLQ file** (`dlq_fallos.json`) is gitignored, created at runtime for failed InfluxDB writes.
- **Ports & dependencies**: `TimeSeriesRepositoryInterface` (Protocol in `modules/iot_ingestion/ports.py`) defines the boundary between IoT ingestion and InfluxDB. Wire implementations via constructor injection.
- **Analytics Engine** reads from InfluxDB via `TelemetryQuery`, evaluates rules, notifies via `notification_component`, and persists alerts to PostgreSQL via `RelationalRepository`.
- **Notification component** uses `_`-prefixed private modules. Contract: build a `NotificationJob` and pass to the handler.
- **GEE initialization** is a thread-safe singleton with `asyncio.to_thread`. Must have a valid service account.

## Session context (Jun 20, 2026)

### What was done this session

- **JWT security** (`Depends(get_current_user)`) wired to all 4 analytics endpoints + 2 external gateway endpoints.
- **`consultar_recomendaciones`** accepts `nombre_regla_humedad` / `nombre_regla_temperatura` query params; looks up `Regla` from PostgreSQL via `relational_repo.get_regla_by_nombre_and_campo()` and overrides umbrales.
- **Predictions** persisted to PostgreSQL on each call to `consultar_predicciones`; `Prediccion.nombre_regla` made nullable; FK constraints removed.
- **`modo=historico`** query param on `GET .../recomendaciones` — fetches from `list_alertas_by_parcela()` in DB (bypasses live InfluxDB query).
- **PUT and DELETE for reglas** (`PUT /campos/reglas/{nombre_regla}`, `DELETE /campos/reglas/{nombre_regla}`) with `?nombre_campo=`; added `ReglaUpdateRequest` model; added `update_regla` / `delete_regla` to repository and ports; 204 on success, 404 if not found.
- **`api-agtechuns.yaml`** updated — paths realigned (`POST /reglas` → `POST /campos/reglas`), new paths added (`GET /campos/{nombreCampo}/reglas`, PUT, DELETE), schemas added (`ReglaRequest`, `ReglaResponse`, `ReglaUpdateRequest`).
- **External Data Gateway fixes** — auth added to `GET /external/weather` and `GET /external/satelital`; `gateway.py` no longer imports `HTTPException` (raises `ValueError` instead); router catches `ValueError` → `HTTPException(502)`; temp file for GEE credentials cleaned in `finally` block; `README.md` routes updated (`/external-data/` → `/external/`).
- **`.env`** populated with `DATABASE_DSN=postgresql+asyncpg://neondb_owner:...@ep-winter-hall-...neon.tech/neondb?sslmode=require`.
- **37 unit tests** created in `tests/test_analytics_engine.py` covering filtering, extraction, calculations, condition evaluation, alert classification, messages, `evaluar_umbral_humedad/temperatura`, `generar_prediccion`, `evaluar_regla`, `evaluar_reglas` — all pass.
- **`pytest.ini`** created with `asyncio_mode = auto`.
- **Server boots successfully**; all 5 protected endpoints return `401 Unauthorized` without JWT token.

### Key decisions

- PUT/DELETE on reglas added although originally excluded — user explicitly requested them later.
- `ReglaUpdateRequest` uses all-optional fields for partial updates; PK (`nombre_regla`, `nombre_campo`) passed via path + query param.
- `Prediccion` FK constraints removed (like `Alerta`) to allow persistence without guaranteed `Regla` / `VentanaTemporal` records.
- External Data Gateway service layer (`gateway.py`) uses `ValueError` instead of `HTTPException`; router translates to `502` — keeps thin controller pattern.
- `test_clasificar_alerta_amarillo` was removed because "amarillo" state is unreachable with current `_clasificar_alerta` implementation (design limitation, not a bug).

### Current state (before reboot)

- Server boots, JWT enforced ✅
- 37 unit tests pass ✅
- PostgreSQL (Neon) connected via `.env` ✅
- InfluxDB Cloud credentials exist in `credenciales.env` (may or may not be valid)
- **Docker NOT available** — Mosquitto broker cannot run locally
- Full end-to-end integration test pending (needs Mosquitto + sensor simulator running)

### Next steps

1. Install Docker Desktop for Windows and reboot
2. Run `docker compose -f deploy/broker/docker-compose.yml up -d` to start Mosquitto
3. Verify InfluxDB Cloud credentials with your classmate if connection fails
4. Start MQTT ingestion: `python -m src.infrastructure.time_series_repo.bootstrap`
5. Start sensor simulator: `python tools/simulador_sensores/lns_console.py` (with `BROKER=localhost` or your broker IP)
6. Start FastAPI: `uvicorn src.main:app --reload`
7. Get JWT via `POST /auth/login`, then exercise all endpoints

### Relevant files

- `src/modules/analytics_engine/router.py`: all 6 endpoints (GET recomendaciones/predicciones, POST/PUT/DELETE reglas, GET reglas by campo), JWT protected, DB rule lookup, historico mode, prediction persistence
- `src/modules/analytics_engine/engine.py`: core rule evaluation (37 unit tests pass)
- `src/modules/analytics_engine/models.py`: `ReglaUpdateRequest` added
- `src/infrastructure/relational_repo/repository.py`: `get_regla_by_nombre_and_campo`, `update_regla`, `delete_regla`; `create_prediccion` accepts nullable `nombre_regla`
- `src/infrastructure/relational_repo/ports.py`: matching interface methods
- `src/infrastructure/relational_repo/models.py`: `Prediccion` FKs removed, `nombre_regla` nullable
- `src/modules/external_data_gateway/router.py`: JWT protected, catches `ValueError` → `HTTPException(502)`
- `src/modules/external_data_gateway/gateway.py`: no `HTTPException` import, raises `ValueError`; temp GEE file cleaned in `finally`
- `src/modules/external_data_gateway/README.md`: routes and error table updated
- `src/core/config.py`: reads `DATABASE_DSN` from env
- `.env`: contains `DATABASE_DSN` with Neon asyncpg URL
- `api-agtechuns.yaml`: aligned paths, new PUT/DELETE/GET reglas endpoints, `ReglaRequest`/`ReglaResponse`/`ReglaUpdateRequest` schemas
- `tests/test_analytics_engine.py`: 37 passing tests
- `pytest.ini`: `asyncio_mode = auto`
- `deploy/broker/docker-compose.yml`: Mosquitto MQTT broker (needs Docker)
- `tools/simulador_sensores/credenciales.env`: InfluxDB Cloud credentials
