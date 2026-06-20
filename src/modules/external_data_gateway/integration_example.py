"""Ejemplo de consumo del External Data Gateway para el equipo de Analytics Engine."""
import asyncio

from modules.external_data_gateway.gateway import (
    fetch_satellite_indices,
    fetch_weather,
)


async def main():
    # 1. Weather
    weather = await fetch_weather(latitude=-33.45, longitude=-66.28)
    print(f"Temp: {weather.temperature_celsius}°C, Hum: {weather.humidity_percent}%")

    # 2. Satellite
    try:
        sat = await fetch_satellite_indices(
            parcel_id="parcela-001",
            latitude=-33.45,
            longitude=-66.28,
        )
        print(f"NDVI: {sat.ndvi:.3f}, NDMI: {sat.ndmi:.3f}, Fecha: {sat.date}")
    except Exception as e:
        print(f"Satélite no disponible: {e}")


asyncio.run(main())
