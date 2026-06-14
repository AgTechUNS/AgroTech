import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
import logging

from IngestionIoT.query_models import TelemetryQuery

load_dotenv("credenciales.env")
logging.getLogger("influxdb_client").setLevel(logging.ERROR)


class TimeSeriesRepository:
    def __init__(self):
        self.url = os.getenv("INFLUX_URL")
        self.token = os.getenv("INFLUX_TOKEN")
        self.org = os.getenv("INFLUX_ORG")
        self.bucket = os.getenv("INFLUX_BUCKET")
        self.client = None

        print(f"[TimeSeriesRepository] Credenciales cargadas:")
        print(f"   URL: {self.url}")
        print(f"   Bucket: {self.bucket}")

    async def initialize(self):
        try:
            print(f"[TimeSeriesRepository] Conectando a InfluxDB...")
            self.client = InfluxDBClientAsync(
                url=self.url, token=self.token, org=self.org, timeout=20000
            )
            ok = await self.client.ping()
            print(f"[TimeSeriesRepository] Conexión exitosa a InfluxDB")
            print(f"   Ping: {ok}")
        except Exception as e:
            print(f"[TimeSeriesRepository] Error al conectar: {e}")
            raise
        return self

    async def guardar_telemetria(self, lectura):
        try:
            if not self.client:
                print(f"Cliente de InfluxDB no inicializado")
                return
            punto = (
                Point("telemetria_sensor")
                .tag("campo_id", lectura.campo_id)
                .tag("id_parcela", lectura.parcela_id)
                .tag("id_sensor", lectura.sensor_id)
                .field("temperatura", lectura.temperatura)
                .field("humedad", lectura.humedad)
                .time(lectura.timestamp)
            )
            write_api = self.client.write_api()
            await write_api.write(bucket=self.bucket, org=self.org, record=punto)
            print(f"Dato guardado para campo {lectura.campo_id} | parcela {lectura.parcela_id} | Sensor: {lectura.sensor_id}")
        except Exception as e:
            print(f"Error al guardar en InfluxDB: {e}")

    # ──────────────────────────────────────────────
    # Consultas públicas
    # ──────────────────────────────────────────────

    async def query(self, spec: TelemetryQuery) -> list[dict]:
        if not self.client:
            raise RuntimeError("TimeSeriesRepository no inicializado")
        flux = self._build_flux(spec)
        return await self.query_raw(flux)

    async def query_raw(self, flux_query: str) -> list[dict]:
        if not self.client:
            raise RuntimeError("TimeSeriesRepository no inicializado")
        query_api = self.client.query_api()
        tables = await query_api.query(org=self.org, query=flux_query)
        return self._tables_to_dicts(tables)

    # ──────────────────────────────────────────────
    # Helpers privados
    # ──────────────────────────────────────────────

    @staticmethod
    def _escape(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    def _build_flux(self, spec: TelemetryQuery) -> str:
        pipes: list[str] = []

        # 1. From + range
        time_from = spec.time_from if spec.time_from else datetime.now(timezone.utc) - timedelta(days=7)
        time_to = spec.time_to if spec.time_to else datetime.now(timezone.utc)
        start = time_from.isoformat().replace("+00:00", "Z")
        stop = time_to.isoformat().replace("+00:00", "Z")
        pipes.append(f'from(bucket: "{self._escape(self.bucket)}")')
        pipes.append(f"range(start: {start}, stop: {stop})")

        # 2. Filtro por measurement
        pipes.append('filter(fn: (r) => r._measurement == "telemetria_sensor")')

        # 3. Filtro por fields
        if spec.fields:
            cond = " or ".join(f'r._field == "{self._escape(f)}"' for f in spec.fields)
            pipes.append(f"filter(fn: (r) => {cond})")

        # 4. Filtro por tags
        if spec.sensors:
            cond = " or ".join(f'r.id_sensor == "{self._escape(s)}"' for s in spec.sensors)
            pipes.append(f"filter(fn: (r) => {cond})")
        if spec.campos:
            cond = " or ".join(f'r.campo_id == "{self._escape(c)}"' for c in spec.campos)
            pipes.append(f"filter(fn: (r) => {cond})")
        if spec.parcelas:
            cond = " or ".join(f'r.id_parcela == "{self._escape(p)}"' for p in spec.parcelas)
            pipes.append(f"filter(fn: (r) => {cond})")

        # 5. Group by antes de agregación (resetea la clave de grupo)
        if spec.group_by is not None:
            cols = ", ".join(f'"{self._escape(c)}"' for c in spec.group_by) if spec.group_by else ""
            pipes.append(f"group(columns: [{cols}])")

        # 6. Agregación por ventana temporal
        if spec.aggregate_window and spec.aggregate_function:
            pipes.append(f"aggregateWindow(every: {spec.aggregate_window}, fn: {spec.aggregate_function})")

        # 7. Pivot: _field → columnas separadas
        if spec.pivot:
            pipes.append('pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")')

        # 8. Orden
        desc = "true" if spec.order == "desc" else "false"
        pipes.append(f'sort(columns: ["_time"], desc: {desc})')

        # 9. Límite
        if spec.limit is not None:
            pipes.append(f"limit(n: {spec.limit})")

        return " |> ".join(pipes)

    @staticmethod
    def _tables_to_dicts(tables) -> list[dict]:
        result: list[dict] = []
        for table in tables:
            for record in table.records:
                row = dict(record.values)
                row.pop("result", None)
                row.pop("table", None)
                result.append(row)
        return result

    async def cerrar_conexion(self):
        if self.client:
            try:
                await self.client.close()
                print(f"[TimeSeriesRepository] Conexión cerrada")
            except Exception as e:
                print(f"Error al cerrar conexión: {e}")


