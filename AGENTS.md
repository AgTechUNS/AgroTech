# AgroTech — Agent Guide

## Project structure

Modular monolith (Python/FastAPI), organized by business domain (Screaming Architecture).

```
src/                        # Python package root (run all commands from repo root)
├── main.py                 # FastAPI entrypoint — only /external-data/* + /health
├── core/config.py          # Env-based settings (dataclass singleton)
├── modules/                # Business domain components
│   ├── iot_ingestion/      # MQTT subscriber + dedup + async workers → InfluxDB
│   ├── analitycs_engine/   # Rule evaluation (heat/hydric stress alerts)
│   ├── external_data_gateway/  # REST endpoints → Open-Meteo + Google Earth Engine
│   ├── notification_component/ # Alert dispatch: in_app / email / sms (Redis dedup)
│   └── security/           # TODO (empty)
└── infrastructure/         # Persistence implementations
    ├── time_series_repo/   # InfluxDB client + Flux query builder
    └── relational_repo/    # TODO (empty)
```

## Running the project

All commands run from repo root. `src/` is implicitly the Python path root — do NOT `cd src/`.

```sh
# FastAPI server (external-data gateway + health)
uvicorn src.main:app --reload
# or: python -m uvicorn src.main:app --reload

# IoT telemetry pipeline (MQTT → InfluxDB)
python -m src.infrastructure.time_series_repo.bootstrap

# Sensor simulator (curses TUI)
python tools/simulador_sensores/lns_console.py

# MQTT broker (Mosquitto via Docker)
docker compose -f deploy/broker/docker-compose.yml up -d
```

## Credentials & env loading

- **InfluxDB**: `tools/simulador_sensores/credenciales.env` is loaded by a **hard-coded relative path** in `src/infrastructure/time_series_repo/influx_client.py:10`. The agent must find and check this file if InfluxDB connection fails.
- **Google Earth Engine**: Service account JSON via `GEE_CREDENTIALS_FILE` (file path) or `GEE_CREDENTIALS_JSON` (inline JSON string). Default file: `~/.agrotech/secrets/service_account.json`.
- **Redis** (notification dedup): `REDIS_URL` env var, default `redis://localhost:6379`.
- `.env` files are gitignored; only `.env.example` is committed. Copy it for local use.

## Architecture notes

- **Three independent runtimes**: FastAPI server, MQTT ingestion bootstrap, and sensor simulator can each run alone. They communicate via MQTT (sensors → ingestion) and InfluxDB (ingestion → analytics).
- **No tests, no CI, no linter/formatter/typechecker configured** — do not assume pytest, ruff, black, mypy, etc.
- **No `pyproject.toml` or `setup.py`** — `src/` is the package root; import paths use absolute module names from there (e.g., `from modules.iot_ingestion.schemas`).
- **MQTT topic**: `v3/agtechuns-app/devices/+/up` (QoS 1). Payload is base64-decoded JSON with fields `{t, h}` (temperature, humidity).
- **DLQ file** (`dlq_fallos.json`) is gitignored, created at runtime for failed InfluxDB writes.
- **Ports & dependencies**: `TimeSeriesRepositoryInterface` (Protocol in `modules/iot_ingestion/ports.py`) defines the boundary between IoT ingestion and InfluxDB. Wire implementations via constructor injection.
- **Analytics Engine** is pure functions (no persistence yet). Reads from InfluxDB via `TelemetryQuery`, evaluates rules, produces `ResultadoPrediccion`.
- **Notification component** uses `_`-prefixed private modules. Contract: build a `NotificationJob` and pass to the handler.
- **GEE initialization** is a thread-safe singleton with `asyncio.to_thread`. Must have a valid service account.
