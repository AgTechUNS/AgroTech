# notification_component/_config.py
"""
Configuración hardcodeada de notificaciones por tipo de evento.

Este archivo concentra todo lo que en una versión futura probablemente
se mueva a una tabla de preferencias en base de datos:
  - qué canales se usan para cada tipo de alerta
  - cómo se renderiza el mensaje para cada uno

Mantenerlo separado de _contracts.py es intencional: los contratos
(forma de los datos) cambian poco, esta configuración va a cambiar
seguido a medida que se agreguen tipos de alerta o se ajuste el copy.
"""

from dataclasses import dataclass
from typing import Callable

from ._contracts import EventType, NotificationJob

Channel = str  # "in_app" | "email" | "sms"

IN_APP = "in_app"
EMAIL = "email"
SMS = "sms"


@dataclass(frozen=True)
class EventConfig:
    """Configuración fija para un tipo de evento."""

    label: str
    icon: str
    channels: tuple[Channel, ...]
    template: Callable[[NotificationJob], str]


def _heat_stress_template(job: NotificationJob) -> str:
    return (
        f"🌡️ Alerta de Calor Extremo: temperatura máxima de {job.value}°C "
        f"detectada en {job.field_id} (umbral: {job.threshold}°C)."
    )


def _hydric_stress_template(job: NotificationJob) -> str:
    return (
        f"💧 Alerta de Estrés Hídrico: humedad promedio de {job.value}% "
        f"en {job.field_id} por debajo del umbral ({job.threshold}%)."
    )


EVENT_CONFIG: dict[EventType, EventConfig] = {
    EventType.HEAT_STRESS: EventConfig(
        label="Calor Extremo",
        icon="🌡️",
        channels=(IN_APP, EMAIL, SMS),
        template=_heat_stress_template,
    ),
    EventType.HYDRIC_STRESS: EventConfig(
        label="Estrés Hídrico",
        icon="💧",
        channels=(IN_APP, EMAIL, SMS),
        template=_hydric_stress_template,
    ),
}


def get_config(event_type: EventType) -> EventConfig:
    """
    Punto único de acceso a la configuración de un evento.

    Lanza KeyError si alguien agrega un EventType nuevo en _contracts.py
    y se olvida de registrar su configuración acá — falla rápido y
    explícito, en vez de silenciosamente no enviar nada.
    """
    return EVENT_CONFIG[event_type]