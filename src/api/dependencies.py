"""Inyección de dependencias del API Controller (FastAPI Depends).

Aquí se resuelven: el contexto de seguridad (provisto por el Security
Controller) y las instancias de los componentes a los que se delega.
"""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .adapters_mock import (MockAnalyticsEngine, MockRelationalRepository,
                            MockTimeSeriesRepository)
from .ports import (AnalyticsEnginePort, ParcelaDTO, RelationalRepositoryPort,
                    Rol, SecurityContext, TimeSeriesRepositoryPort)

# Singletons en memoria: mantienen los datos entre requests durante la sesión.
_relational = MockRelationalRepository()
_timeseries = MockTimeSeriesRepository()
_analytics = MockAnalyticsEngine()


def get_relational_repo() -> RelationalRepositoryPort:
    return _relational


def get_timeseries_repo() -> TimeSeriesRepositoryPort:
    return _timeseries


def get_analytics_engine() -> AnalyticsEnginePort:
    return _analytics


# --- Security Controller (STUB) -------------------------------------------
# TODO: reemplazar por la dependencia real del componente Security Controller
# (rama Auth-and-Security-Controller): decodificar el JWT con python-jose,
# verificar firma y expiración, e inyectar el contexto del usuario.
# Token de prueba (DEV): "admin"  |  "agronomo"  |  "agronomo:c1,c2"
async def get_security_context(
    authorization: str | None = Header(default=None),
) -> SecurityContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Falta el token Bearer.")
    token = authorization[len("Bearer "):].strip()
    if token in ("admin", "Administrador"):
        return SecurityContext("u-admin", Rol.ADMINISTRADOR, ())
    if token.lower().startswith("agronomo") or token.startswith("Agrónomo"):
        campos: tuple[str, ...] = ()
        if ":" in token:
            campos = tuple(c.strip() for c in token.split(":", 1)[1].split(",") if c.strip())
        return SecurityContext("u-agronomo", Rol.AGRONOMO, campos or ("c1",))
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido.")


# --- RBAC ------------------------------------------------------------------
def requiere_rol(*roles: Rol):
    """RBAC a nivel de operación (ej. crear campo = solo Administrador)."""
    async def _dep(ctx: SecurityContext = Depends(get_security_context)) -> SecurityContext:
        if ctx.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Rol sin permisos para esta operación.")
        return ctx
    return _dep


def verificar_acceso_campo(ctx: SecurityContext, campo_id: str) -> None:
    """RBAC a nivel de recurso: un Agrónomo solo opera sobre campos asignados."""
    if ctx.es_admin:
        return
    if campo_id not in ctx.campos_asignados:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "El agrónomo no tiene asignado este campo.")


def verificar_acceso_parcela(ctx: SecurityContext, parcela: ParcelaDTO) -> None:
    verificar_acceso_campo(ctx, parcela.campo_id)
