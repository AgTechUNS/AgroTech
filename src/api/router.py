"""Composición del API Controller y su integración con la app FastAPI."""
from __future__ import annotations

from fastapi import APIRouter, FastAPI

from .controllers import campos, cultivos, parcelas, predicciones, reportes
from .middleware import PerformanceTrackingMiddleware

api_router = APIRouter()
for _modulo in (campos, parcelas, cultivos, predicciones, reportes):
    api_router.include_router(_modulo.router)


def registrar_api(app: FastAPI) -> None:
    """Punto de integración del API Controller con main.py."""
    app.add_middleware(PerformanceTrackingMiddleware)  # PER-02
    app.include_router(api_router)
