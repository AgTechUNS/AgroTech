import asyncio
import os
import signal
from dotenv import load_dotenv
from modules.iot_ingestion.mqtt_subscriber import IotIngestionService

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from infrastructure.time_series_repo.influx_client import TimeSeriesRepository


async def main():
    repositorio_real = await TimeSeriesRepository().initialize()

    ingestion_component = IotIngestionService(
        broker_url=os.getenv("BROKER", "localhost"),
        port=int(os.getenv("PORT", "1883")),
        repository=repositorio_real
    )

    stop_event = asyncio.Event()

    def _handle_signal():
        print("\n[Signal] Apagando sistema...")
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            pass  # Windows no soporta add_signal_handler

    try:
        print("Iniciando sistema integral de telemetría...")
        ingestion_component.start_workers(loop)
        try:
            ingestion_component.start()
        except ConnectionRefusedError:
            print("[Bootstrap] ERROR: No se pudo conectar al broker MQTT en localhost:1883.")
            print("[Bootstrap] Asegurate de que Mosquitto (Docker) esté corriendo:")
            print("[Bootstrap]   docker compose -f deploy/broker/docker-compose.yml up -d")
            print("[Bootstrap] Saliendo...")
            return
        print("[Bootstrap] Ingestion corriendo. Presioná Ctrl+C para detener.")
        await stop_event.wait()
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] Apagando sistema...")
    finally:
        ingestion_component.stop()
        await repositorio_real.cerrar_conexion()
        print("[Bootstrap] Sistema detenido.")


if __name__ == "__main__":
    asyncio.run(main())
