import json

from fastapi import APIRouter, HTTPException, Query

from .gateway import (
    _ndmi_a_humedad_suelo,
    fetch_satellite_indices,
    fetch_weather,
    parsear_coordenadas,
)
from .models import SatelitalResponse, WeatherResponse

router = APIRouter(prefix="/external", tags=["External Data Gateway"])


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitud (-90 a 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud (-180 a 180)"),
):
    return await fetch_weather(lat, lon)


@router.get("/satelital", response_model=SatelitalResponse)
async def get_satelital(
    coordenadas: str = Query(
        ..., description="GeoJSON Point o Polygon con los límites de consulta"
    ),
):
    try:
        lat, lon = parsear_coordenadas(coordenadas)
    except (ValueError, json.JSONDecodeError, KeyError, IndexError):
        raise HTTPException(
            status_code=400,
            detail="GeoJSON inválido: se espera un objeto Point o Polygon con coordenadas válidas",
        )
    sat = await fetch_satellite_indices("", lat, lon)
    return SatelitalResponse(
        ndvi=sat.ndvi,
        humedad_suelo_estimada=_ndmi_a_humedad_suelo(sat.ndmi),
    )
