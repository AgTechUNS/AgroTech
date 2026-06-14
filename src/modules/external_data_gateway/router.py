from fastapi import APIRouter, Path, Query

from .gateway import fetch_satellite_indices, fetch_weather
from .models import SatelliteResponse, WeatherResponse

router = APIRouter(prefix="/external-data", tags=["External Data Gateway"])


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitud (-90 a 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud (-180 a 180)"),
):
    return await fetch_weather(lat, lon)


@router.get("/satellite/{parcel_id}", response_model=SatelliteResponse)
async def get_satellite(
    parcel_id: str = Path(..., description="Identificador único de la parcela"),
    lat: float = Query(..., ge=-90, le=90, description="Latitud (-90 a 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud (-180 a 180)"),
):
    return await fetch_satellite_indices(parcel_id, lat, lon)
