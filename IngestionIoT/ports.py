from typing import Protocol
from IngestionIoT.domain_models import LecturaNormalizada
from IngestionIoT.query_models import TelemetryQuery

class TimeSeriesRepositoryInterface(Protocol):
    async def guardar_telemetria(self, lectura: LecturaNormalizada) -> None:
        ...

    async def query(self, spec: TelemetryQuery) -> list[dict]:
        ...

    async def query_raw(self, flux_query: str) -> list[dict]:
        ...