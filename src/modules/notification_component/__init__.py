"""
Punto de entrada público del Notification Component.

Otros módulos del monolito (Analytics Engine, API Controller,
Reset Password Controller) SOLO deben importar desde aquí.
Nunca desde los submódulos con prefijo _ (privados).
"""

from ._contracts import EventType, NotificationJob
from ._handler import notify
from ._providers._websocket import set_socketio_instance

__all__ = [
    "notify",
    "NotificationJob",
    "EventType",
    "set_socketio_instance",
]