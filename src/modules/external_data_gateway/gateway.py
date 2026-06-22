import asyncio
import json
import logging
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

_CACHE_TTL = int(os.getenv("GEE_CACHE_TTL", "3600"))
_cache: dict[str, tuple[datetime, SatelliteResponse]] = {}
_cache_lock = threading.Lock()

logger = logging.getLogger(__name__)


def _cache_key(lat: float, lon: float) -> str:
    return f"{lat:.4f}:{lon:.4f}"


def _get_cached(lat: float, lon: float) -> SatelliteResponse | None:
    key = _cache_key(lat, lon)
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        ts, resp = entry
        if (datetime.now(timezone.utc) - ts).total_seconds() > _CACHE_TTL:
            del _cache[key]
            return None
        return resp


def _set_cached(lat: float, lon: float, resp: SatelliteResponse):
    key = _cache_key(lat, lon)
    with _cache_lock:
        _cache[key] = (datetime.now(timezone.utc), resp)


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


def _extract_project_id(creds_path: str) -> str | None:
    """Intenta leer project_id del JSON de la service account."""
    try:
        with open(creds_path) as f:
            data = json.load(f)
        return data.get("project_id")
    except (OSError, json.JSONDecodeError):
        return None


def _ensure_ee():
    global _ee_initialized
    if _ee_initialized:
        return
    with _ee_lock:
        if _ee_initialized:
            return
        creds_path = _resolve_gee_credentials()
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                f"Archivo de credenciales GEE no encontrado: {creds_path}"
            )
        try:
            credentials = ee.ServiceAccountCredentials(None, creds_path)
            project_id = GEE_PROJECT_ID or _extract_project_id(creds_path)
            ee.Initialize(credentials, project=project_id)
            _ee_initialized = True
        except Exception as e:
            print(f"[GEE] Error al inicializar Earth Engine: {e}")
            raise
        finally:
            if GEE_CREDENTIALS_JSON:
                try:
                    os.remove(creds_path)
                except OSError:
                    pass


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
    cached = _get_cached(latitude, longitude)
    if cached is not None:
        return cached

    logger.debug("GEE cache MISS for (%.4f, %.4f)", latitude, longitude)

    try:
        await asyncio.to_thread(_ensure_ee)
    except (FileNotFoundError, OSError) as e:
        raise ValueError(f"Capa satelital no disponible: {e}")

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
        raise ValueError("Capa satelital no disponible temporalmente")

    ndvi_value, ndmi_value, epoch_ms = result

    response = SatelliteResponse(
        parcel_id=parcel_id,
        ndvi=ndvi_value,
        ndmi=ndmi_value,
        date=datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc),
        source="Google Earth Engine",
    )
    _set_cached(latitude, longitude, response)
    logger.debug("GEE cache SET for (%.4f, %.4f)", latitude, longitude)
    return response


def _ndmi_a_humedad_suelo(ndmi: float) -> float:
    return round((ndmi + 1) * 50, 2)


def parsear_coordenadas(coordenadas: str) -> tuple[float, float]:
    data = json.loads(coordenadas)
    geom_type = data.get("type", "")

    if geom_type == "Feature":
        geometry = data.get("geometry", {})
        return parsear_coordenadas(json.dumps(geometry))

    coords = data.get("coordinates", [])

    if geom_type == "Point":
        lon, lat = coords
        return lat, lon

    if geom_type == "Polygon":
        todas_lon = [c[0] for ring in coords for c in ring]
        todas_lat = [c[1] for ring in coords for c in ring]
        lat = sum(todas_lat) / len(todas_lat)
        lon = sum(todas_lon) / len(todas_lon)
        return lat, lon

    raise ValueError(f"Tipo de geometría no soportado: {geom_type}")
