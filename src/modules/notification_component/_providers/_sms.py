"""
Provider de SMS via Twilio.

Igual que _email.py, el SDK de Twilio es sincrónico. Se usa
asyncio.to_thread para no bloquear el event loop del monolito
mientras se espera la respuesta HTTP de Twilio.
"""

import asyncio
import os

from twilio.rest import Client

_ALERT_PHONE = os.environ.get("ALERT_PHONE", "+5491112345678")


def _get_client() -> Client:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    return Client(account_sid, auth_token)


async def send_sms(message: str) -> None:
    """Envía un SMS vía Twilio."""
    client = _get_client()
    from_number = os.environ["TWILIO_FROM"]

    await asyncio.to_thread(
        client.messages.create,
        body=message,
        from_=from_number,
        to=_ALERT_PHONE,
    )