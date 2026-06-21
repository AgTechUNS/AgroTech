"""
Audit logging para notificaciones.

Registra en el logger estándar cada intento de envío (exitoso o fallido).
En una versión futura podría persistirse a PostgreSQL para trazabilidad.
"""

import logging

from ._contracts import NotificationJob

logger = logging.getLogger(__name__)


async def log_notification(
    job: NotificationJob,
    channel: str,
    status: str,
    provider: str,
    error: str | None = None,
) -> None:
    """
    Registra un intento de notificación en los logs.
    
    Args:
        job: El trabajo de notificación original.
        channel: Canal usado ("in_app", "email", "sms").
        status: "SENT" o "FAILED".
        provider: Proveedor usado ("websocket", "sendgrid", "twilio").
        error: Mensaje de error si falló, None si fue exitoso.
    """
    extra = {
        "event_type": job.event_type.value,
        "field_id": job.field_id,
        "value": job.value,
        "threshold": job.threshold,
        "channel": channel,
        "provider": provider,
        "status": status,
    }
    if error:
        extra["error"] = error
        logger.warning(
            "Notificación %s falló [%s/%s]: %s",
            job.event_type.value, channel, provider, error,
            extra=extra,
        )
    else:
        logger.info(
            "Notificación %s enviada [%s/%s]",
            job.event_type.value, channel, provider,
            extra=extra,
        )
