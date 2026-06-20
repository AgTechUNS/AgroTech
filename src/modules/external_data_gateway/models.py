from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer


def _ensure_utc(v: datetime | str) -> datetime:
    if isinstance(v, str):
        v = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)


UTCDatetime = Annotated[
    datetime,
    BeforeValidator(_ensure_utc),
    PlainSerializer(
        lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        return_type=str,
    ),
]


class WeatherResponse(BaseModel):
    temperature_celsius: float
    humidity_percent: float
    timestamp: UTCDatetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class SatelliteResponse(BaseModel):
    parcel_id: str
    ndvi: float = Field(..., ge=-1, le=1)
    ndmi: float = Field(..., ge=-1, le=1)
    date: UTCDatetime
    source: Literal["Google Earth Engine"]
