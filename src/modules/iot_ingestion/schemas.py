from dataclasses import dataclass
from datetime import datetime

@dataclass
class LecturaNormalizada:
    """
    Este es el contrato estandarizado.
    Representa una lectura de sensor ya validada y transformada, lista para ser almacenada en una base de datos NoSQL.
    """
    sensor_id: str
    campo_id: str
    parcela_id: str
    temperatura: float
    humedad: float
    timestamp: datetime