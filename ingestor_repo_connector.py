import asyncio
from IngestionIoT.iot_ingestion import IotIngestionService
# Importamos la clase real que hizo tu compañero
from TimeSeriesRepository import TimeSeriesRepository 

async def main():
    # 1. Inicializamos el repositorio REAL de tu compañero dentro del event loop
    repositorio_real = await TimeSeriesRepository().initialize()
    
    # 2. Instanciamos tu componente pasándole el repositorio real
    ingestion_component = IotIngestionService(
        broker_url="localhost",
        port=1883,
        repository=repositorio_real 
    )
    
    try:
        # 3. Arrancamos el servicio
        print("Iniciando sistema integral de telemetría...")
        ingestion_component.start()
    except KeyboardInterrupt:
        print("\nApagando sistema...")
    finally:
        # Limpieza asincrónica al salir
        await repositorio_real.cerrar_conexion()

if __name__ == "__main__":
    asyncio.run(main())