"""
Provider de SMS via Twilio.

El SDK de Twilio es sincrónico, así que send_sms() lo envuelve en
asyncio.to_thread para no bloquear el event loop del monolito mientras
se espera la respuesta HTTP de Twilio.

Espejo de _email.py: las credenciales y números se leen a nivel módulo
(no dentro de la función) para que sean testeables vía patch y para que
el componente falle rápido y explícito si falta configuración, en vez
de tirar un KeyError opaco a mitad del envío.
"""

import asyncio
import os

_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
_TWILIO_FROM = os.getenv("TWILIO_FROM")


def _get_client():
    from twilio.rest import Client

    if not _ACCOUNT_SID or not _AUTH_TOKEN:
        raise ValueError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN no están configuradas")
    return Client(_ACCOUNT_SID, _AUTH_TOKEN)


async def send_sms(message: str, recipient_phone: str) -> None:
    """Envía un SMS vía Twilio."""
    if not _TWILIO_FROM:
        raise ValueError("TWILIO_FROM no está configurada")
    if not recipient_phone:
        raise ValueError("recipient_phone no está configurado")

    client = _get_client()

    await asyncio.to_thread(
        client.messages.create,
        body=message,
        from_=_TWILIO_FROM,
        to=recipient_phone,
    )
    print(f"[Notification] SMS enviado a {recipient_phone} desde {_TWILIO_FROM}")
