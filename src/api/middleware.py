"""Middleware de rendimiento — verifica el objetivo PER-02 (<= 4 s)."""
from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_controller.performance")
PER_02_LIMITE_S = 4.0


class PerformanceTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        inicio = time.perf_counter()
        respuesta = await call_next(request)
        elapsed = time.perf_counter() - inicio
        respuesta.headers["X-Process-Time"] = f"{elapsed:.3f}"
        if elapsed > PER_02_LIMITE_S:
            logger.warning("PER-02 excedido: %s %s tardó %.3f s",
                           request.method, request.url.path, elapsed)
        return respuesta
