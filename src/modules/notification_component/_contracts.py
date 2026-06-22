"""
Contratos públicos del Notification Component.

Este es el ÚNICO archivo que define la forma de los datos que entran
y salen del componente. Cualquier otro módulo del monolito que quiera
notificar algo debe construir un NotificationJob usando estos tipos.

No agregar lógica de negocio aquí — solo definiciones de datos.
"""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """
    Tipos de evento soportados por el sistema de alertas.

    Hereda de str para que la serialización a JSON / DB sea directa
    (EventType.HEAT_STRESS == "heat_stress" da True).
    """

    HEAT_STRESS = "heat_stress"
    HYDRIC_STRESS = "hydric_stress"


class NotificationJob(BaseModel):
    """
    Representa una solicitud de notificación.

    Es la única forma de dato que el Analytics Engine (o cualquier
    otro caller interno) necesita construir para disparar una alerta.
    """

    event_type: EventType
    recipient_id: str = Field(..., description="Identificador del agricultor destinatario")
    recipient_email: str = Field(..., description="Correo electrónico del destinatario")
    recipient_phone: str = Field(default="", description="Teléfono del destinatario en formato E.164 (opcional, SMS falla silenciosamente si está vacío)")
    field_id: str = Field(..., description="Identificador del lote, ej: 'lote-4'")
    value: float = Field(..., description="Valor medido que disparó la alerta")
    threshold: float = Field(..., description="Umbral configurado que fue cruzado")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
