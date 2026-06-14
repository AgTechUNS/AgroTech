import asyncio
import json
import os
import tempfile
import threading
from datetime import datetime, timezone

import ee
import httpx

from .models import SatelliteResponse, WeatherResponse

OPEN_METEO_URL = os.getenv(
    "OPEN_METEO_URL",
    "https://api.open-meteo.com/v1/forecast",
)

GEE_CREDENTIALS_FILE = os.getenv("GEE_CREDENTIALS_FILE", "")
GEE_CREDENTIALS_JSON = os.getenv("GEE_CREDENTIALS_JSON", "")
GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", None)
GEE_COLLECTION_NAME = os.getenv(
    "GEE_COLLECTION_NAME",
    "COPERNICUS/S2_SR_HARMONIZED",
)

_ee_initialized = False
_ee_lock = threading.Lock()


def _resolve_gee_credentials() -> str:
    if GEE_CREDENTIALS_JSON:
        creds_dict = json.loads(GEE_CREDENTIALS_JSON)
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(creds_dict, tmp)
        tmp.close()
        return tmp.name
    if GEE_CREDENTIALS_FILE:
        return GEE_CREDENTIALS_FILE
    default = os.path.expanduser("~/.agrotech/secrets/service_account.json")
    return default


def _ensure_ee():
    global _ee_initialized
    if _ee_initialized:
        return
    with _ee_lock:
        if _ee_initialized:
            return
        creds_path = _resolve_gee_credentials()
        credentials = ee.ServiceAccountCredentials(None, creds_path)
        ee.Initialize(credentials, project=GEE_PROJECT_ID)
        _ee_initialized = True


async def fetch_weather(latitude: float, longitude: float) -> WeatherResponse:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "UTC",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    current = payload["current"]

    return WeatherResponse(
        temperature_celsius=current["temperature_2m"],
        humidity_percent=current["relative_humidity_2m"],
        timestamp=current["time"],
        latitude=latitude,
        longitude=longitude,
    )


async def fetch_satellite_indices(
    parcel_id: str,
    latitude: float,
    longitude: float,
) -> SatelliteResponse:
    await asyncio.to_thread(_ensure_ee)

    point = ee.Geometry.Point([longitude, latitude])

    def _compute():
        collection = (
            ee.ImageCollection(GEE_COLLECTION_NAME)
            .filterBounds(point)
            .sort("system:time_start", False)
        )

        size = collection.size().getInfo()
        if size == 0:
            return None

        latest = collection.first()
        ndvi = latest.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndmi = latest.normalizedDifference(["B8", "B11"]).rename("NDMI")

        ndvi_value = (
            ndvi.sample(point, scale=10)
            .first()
            .get("NDVI")
            .getInfo()
        )
        ndmi_value = (
            ndmi.sample(point, scale=10)
            .first()
            .get("NDMI")
            .getInfo()
        )

        epoch_ms = latest.get("system:time_start").getInfo()
        return ndvi_value, ndmi_value, epoch_ms

    result = await asyncio.to_thread(_compute)

    if result is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail="Capa satelital no disponible temporalmente",
        )

    ndvi_value, ndmi_value, epoch_ms = result

    return SatelliteResponse(
        parcel_id=parcel_id,
        ndvi=ndvi_value,
        ndmi=ndmi_value,
        date=datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc),
        source="Google Earth Engine",
    )
