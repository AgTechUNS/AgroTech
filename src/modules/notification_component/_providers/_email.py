"""
Provider de email via SendGrid.

Este es uno de los dos puntos del componente que cruza una frontera
de red real hacia un SaaS externo (el otro es _sms.py). Si SendGrid
está caído o las credenciales son inválidas, la excepción se propaga
hacia _handler.py, que ya sabe capturarla con asyncio.gather(...,
return_exceptions=True) sin tumbar los demás canales.
"""

import asyncio
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

_SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
_ALERT_EMAIL = os.getenv("ALERT_EMAIL", "admin@agtech.com")
_FROM_EMAIL = os.getenv("SENDGRID_FROM", "alertas@agtech.com")


async def send_email(message: str, subject: str) -> None:
    """
    Envía un email vía SendGrid.

    El SDK de SendGrid es sincrónico (no tiene cliente async nativo),
    por eso se ejecuta en un thread pool con asyncio.to_thread para no
    bloquear el event loop mientras espera la respuesta HTTP.
    """
    if not _SENDGRID_API_KEY:
        raise ValueError("SENDGRID_API_KEY no está configurada")
    
    client = SendGridAPIClient(_SENDGRID_API_KEY)

    mail = Mail(
        from_email=_FROM_EMAIL,
        to_emails=_ALERT_EMAIL,
        subject=f"⚠️ AgTechUNS — {subject}",
        plain_text_content=message,
    )

    await asyncio.to_thread(client.send, mail)