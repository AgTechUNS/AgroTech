# notification_component/_deduplication.py
"""
Deduplicación de alertas repetitivas en memoria.

Evita que el mismo tipo de evento, para el mismo lote, dispare
notificaciones múltiples veces dentro de una ventana de tiempo corta
(ej. el Analytics Engine vuelve a evaluar el umbral cada minuto y
sigue estando por encima/debajo).

Usa un dict en memoria con timestamps. No requiere Redis ni ninguna
infraestructura externa — adecuado para un monolito de un solo proceso.
"""

import asyncio
import time

from ._contracts import NotificationJob

_TTL_SECONDS = 30 * 60  # 30 minutos: ventana de deduplicación

_seen: dict[str, float] = {}
_lock = asyncio.Lock()


def _dedup_key(job: NotificationJob) -> str:
    return f"{job.event_type.value}:{job.field_id}:{job.threshold}"


async def is_duplicate(job: NotificationJob) -> bool:
    """
    Devuelve True si ya se procesó un evento igual (mismo tipo +
    mismo lote) dentro de los últimos 30 minutos.

    La operación es atómica gracias a un asyncio.Lock: garantiza que
    solo un caller puede ganar si dos eventos llegan al mismo tiempo
    para el mismo lote — no hay race condition posible.
    """
    key = _dedup_key(job)
    now = time.time()

    async with _lock:
        last = _seen.get(key)
        if last is not None and (now - last) < _TTL_SECONDS:
            return True

        _seen[key] = now
        return False