# notification_component/_deduplication.py
"""
Deduplicación de alertas repetitivas usando Redis.

Evita que el mismo tipo de evento, para el mismo lote, dispare
notificaciones múltiples veces dentro de una ventana de tiempo corta
(ej. el Analytics Engine vuelve a evaluar el umbral cada minuto y
sigue estando por encima/debajo).

La operación es atómica gracias a SET ... NX: Redis garantiza que
solo un caller puede "ganar" la escritura si dos eventos llegan al
mismo tiempo para el mismo lote — no hay race condition posible.
"""

import os
from typing import Any

from ._contracts import NotificationJob

_TTL_SECONDS = 30 * 60  # 30 minutos: ventana de deduplicación

_redis_client: Any = None


def _get_client() -> Any:
    """
    Lazy singleton: la conexión se crea recién en el primer uso,
    no al importar el módulo. Esto evita fallar al importar el
    paquete si Redis todavía no está disponible (ej. en tests).
    """
    import redis.asyncio as redis

    global _redis_client
    if _redis_client is None:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


def _dedup_key(job: NotificationJob) -> str:
    return f"dedup:{job.event_type.value}:{job.recipient_id}:{job.field_id}"


async def is_duplicate(job: NotificationJob) -> bool:
    """
    Devuelve True si ya se procesó un evento igual (mismo tipo +
    mismo lote) dentro de los últimos 30 minutos.

    SET key value EX ttl NX:
      - NX = solo escribe si la key NO existe
      - Si la key ya existía, Redis devuelve None -> es un duplicado
      - Si la key no existía, Redis la crea y devuelve True -> no lo es
    """
    client = _get_client()
    key = _dedup_key(job)
    was_set = await client.set(key, "1", ex=_TTL_SECONDS, nx=True)
    return was_set is None
