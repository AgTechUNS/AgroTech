"""
Provider de notificaciones in-app via WebSocket (Socket.IO).

A diferencia de _email.py y _sms.py, este módulo NO crea su propio
servidor — recibe una instancia de socketio.AsyncServer que ya vive
en la capa HTTP compartida del monolito (inicializada junto con FastAPI).

set_socketio_instance() se llama UNA SOLA VEZ al arrancar el monolito.
send_in_app() se llama en cada notificación, usando esa instancia.

Esta es la única frontera de red real de este provider: el destino
es la SPA en el browser del usuario, un proceso distinto en otra
máquina — no otro módulo del monolito.
"""

from typing import Any

_sio: Any | None = None


def set_socketio_instance(sio: Any) -> None:
    """
    Inyecta la instancia compartida de Socket.IO.

    Se llama desde el bootstrap del monolito (ej. main.py de FastAPI),
    no desde el flujo normal de notificación.
    """
    global _sio
    _sio = sio


async def send_in_app(recipient_id: str, field_id: str, message: str) -> None:
    """Emite una alerta in-app al usuario destinatario."""
    if _sio is None:
        raise RuntimeError(
            "Socket.IO no inicializado: llamar set_socketio_instance() "
            "en el bootstrap del monolito antes de notificar."
        )
    await _sio.emit("alert", {"recipient_id": recipient_id, "field_id": field_id, "message": message}, room=recipient_id)