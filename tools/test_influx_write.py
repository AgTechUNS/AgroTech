"""Write test telemetry directly to InfluxDB (bypass MQTT)."""
import asyncio, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from datetime import datetime, timezone, timedelta
from influxdb_client import Point
from infrastructure.time_series_repo.influx_client import TimeSeriesRepository


async def main():
    repo = await TimeSeriesRepository().initialize()

    # Write 3 test readings
    now = datetime.now(timezone.utc)
    readings = [
        (now - timedelta(minutes=10), "CampoY", "PY", "sensor-test-1", 42.0, 10.0),
        (now - timedelta(minutes=5),  "CampoY", "PY", "sensor-test-2", 25.0, 65.0),
        (now - timedelta(minutes=2),  "CampoY", "PY", "sensor-test-1", 41.5, 11.0),
    ]

    write_api = repo.client.write_api()
    for ts, campo, parcela, sensor, temp, hum in readings:
        punto = (
            Point("telemetria_sensor")
            .tag("campo_id", campo)
            .tag("id_parcela", parcela)
            .tag("id_sensor", sensor)
            .field("temperatura", temp)
            .field("humedad", hum)
            .time(ts)
        )
        await write_api.write(bucket=repo.bucket, org=repo.org, record=punto)
        print(f"  Escrito: {sensor} t={temp} h={hum} @ {ts.isoformat()}")

    # Verify by querying back
    from modules.iot_ingestion.query_models import TelemetryQuery
    query = TelemetryQuery(
        campos=["CampoY"],
        parcelas=["PY"],
        time_from=now - timedelta(hours=1),
        pivot=True,
    )
    rows = await repo.query(query)
    print(f"\nQuery result: {len(rows)} rows")
    for r in rows[:5]:
        print(f"  {r.get('_time')} campo={r.get('campo_id')} parcela={r.get('id_parcela')} t={r.get('temperatura')} h={r.get('humedad')}")

    await repo.cerrar_conexion()


asyncio.run(main())
