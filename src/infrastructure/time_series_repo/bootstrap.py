import asyncio
from modules.iot_ingestion.mqtt_subscriber import IotIngestionService
from infrastructure.time_series_repo.influx_client import TimeSeriesRepository

async def main():
    repositorio_real = await TimeSeriesRepository().initialize()
    
    ingestion_component = IotIngestionService(
        broker_url="localhost",
        port=1883,
        repository=repositorio_real
    )
    
    try:
        print("Iniciando sistema integral de telemetría...")
        ingestion_component.start()
    except KeyboardInterrupt:
        print("\nApagando sistema...")
    finally:
        await repositorio_real.cerrar_conexion()

if __name__ == "__main__":
    asyncio.run(main())
