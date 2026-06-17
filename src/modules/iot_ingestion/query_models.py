from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class TelemetryQuery:
    sensors: list[str] | None = None
    campos: list[str] | None = None
    parcelas: list[str] | None = None
    fields: list[str] | None = None
    time_from: datetime | None = None
    time_to: datetime | None = None
    aggregate_window: str | None = None
    aggregate_function: Literal["mean", "max", "min", "last", "first", "count", "sum"] | None = None
    group_by: list[str] | None = None
    pivot: bool = False
    limit: int | None = None
    order: Literal["asc", "desc"] = "desc"
