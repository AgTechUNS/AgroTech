# notification_component/_handler.py
"""
Orquestador principal del Notification Component.

notify() es la única función que el resto del monolito necesita conocer.
Define el ORDEN fijo de la orquestación:

    1. Deduplicación   — ¿ya se mandó esta alerta hace poco?
    2. Templating      — convertir el job crudo en un mensaje legible
    3. Dispatch        — enviar por los 3 canales en paralelo
    4. Audit log       — registrar el resultado de cada canal

Ningún otro módulo del paquete decide este orden — vive solo acá.
"""

import asyncio
import logging

from ._audit import log_notification
from ._config import EMAIL, IN_APP, SMS, get_config
from ._contracts import NotificationJob
from ._deduplication import is_duplicate
from ._providers._email import send_email
from ._providers._sms import send_sms
from ._providers._websocket import send_in_app

logger = logging.getLogger(__name__)


async def notify(job: NotificationJob) -> None:
    """
    Punto de entrada único para disparar una notificación.

    No lanza excepción si un canal individual falla — cada canal se
    intenta de forma independiente y se registra su resultado. Solo
    se interrumpe todo el flujo si el evento es un duplicado reciente.
    """
    if await is_duplicate(job):
        return

    config = get_config(job.event_type)
    message = config.template(job)

    if not job.recipient_id:
        raise ValueError("recipient_id no está configurado")

    results = await asyncio.gather(
        send_in_app(job.recipient_id, job.field_id, message),
        send_email(message, config.label, job.recipient_email),
        send_sms(message, job.recipient_phone),
        return_exceptions=True,
    )

    channel_providers = [
        (IN_APP, "websocket"),
        (EMAIL, "sendgrid"),
        (SMS, "twilio"),
    ]

    for result, (channel, provider) in zip(results, channel_providers):
        failed = isinstance(result, Exception)
        await log_notification(
            job=job,
            channel=channel,
            status="FAILED" if failed else "SENT",
            provider=provider,
            error=str(result) if failed else None,
        )
