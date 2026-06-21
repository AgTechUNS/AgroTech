# External Data Gateway — Guía de Integración

## Propósito
Único módulo autorizado para consumir APIs externas.
Aísla al resto del monolito de fallas, latencias y cambios de formato de proveedores.

## Endpoints expuestos

| Método | Ruta | Responsabilidad |
|--------|------|----------------|
| GET | `/external/weather` | Temperatura y humedad desde Open-Meteo |
| GET | `/external/satelital` | NDVI y NDMI desde Google Earth Engine |

## Consumo desde otros módulos

### Opción recomendada: import directo (mismo event loop)

```python
from modules.external_data_gateway.gateway import fetch_weather, fetch_satellite_indices

# Weather
weather = await fetch_weather(latitude=-33.45, longitude=-66.28)
# → WeatherResponse(temperature_celsius=6.8, humidity_percent=76.0, timestamp=..., latitude=-33.45, longitude=-66.28)

# Satellite
sat = await fetch_satellite_indices(
    parcel_id="parcela-001", latitude=-33.45, longitude=-66.28,
)
# → SatelliteResponse(parcel_id="parcela-001", ndvi=0.42, ndmi=-0.15, date=..., source="Google Earth Engine")
```

### Opción alternativa: vía HTTP (si en el futuro se separa a un servicio)

```python
import httpx

async with httpx.AsyncClient() as client:
    r = await client.get(
        "http://gateway/external/weather",
        params={"lat": -33.45, "lon": -66.28},
    )
    data = r.json()  # WeatherResponse
```

## Manejo de errores

| Código | Significado | Causa |
|--------|-------------|-------|
| 200 | OK | Datos disponibles |
| 400 | GeoJSON inválido | El formato de coordenadas no es válido |
| 502 | Satélite no disponible | Sin imagen satelital para la coordenada / ventana de tiempo |
| 500 | Error externo | Open-Meteo o GEE no respondieron |

## Variables de entorno requeridas

Ver `.env.example` en la raíz del proyecto.

## Diagrama de integración

```
Otros Módulos (Analytics, IoT, ...)
       │
       ├── import → fetch_weather(lat, lon)
       │                └── httpx → Open-Meteo API
       │
       └── import → fetch_satellite_indices(parcel_id, lat, lon)
                        └── ee (asyncio.to_thread) → Google Earth Engine
```
