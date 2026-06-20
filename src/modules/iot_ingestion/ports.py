from typing import Protocol
from modules.iot_ingestion.schemas import LecturaNormalizada
from modules.iot_ingestion.query_models import TelemetryQuery

class TimeSeriesRepositoryInterface(Protocol):
    async def guardar_telemetria(self, lectura: LecturaNormalizada) -> None:
        ...

    async def query(self, spec: TelemetryQuery) -> list[dict]:
        ...

    async def query_raw(self, flux_query: str) -> list[dict]:
        ...
