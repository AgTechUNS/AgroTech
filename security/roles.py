"""
roles.py — Lógica RBAC y control de acceso a nivel de recurso.

Responsabilidades:
  - RoleEnum         : fuente de verdad de roles (importado desde core/enums).
  - require_role()   : dependencia inyectable que verifica el rol mínimo.
  - verify_field_access() : verifica que el usuario tenga acceso al campo solicitado.

Separación de intereses:
  Toda regla de permisos vive acá. Si mañana se agrega un nuevo rol
  o cambian las políticas, el cambio es en un solo archivo.

Flujo de autorización:
  get_current_user() → UserContext → require_role() → verify_field_access()
"""

import logging
from typing import Callable

from fastapi import Depends

from core.enums import RoleEnum
from core.exceptions import InsufficientPermissionsException, ResourceOwnershipException
from security.schemas import UserContext
from security.get_current_user import get_current_user

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Re-exportar RoleEnum desde core/enums
# ──────────────────────────────────────────────
# Los consumidores de security/ importan RoleEnum desde acá,
# sin necesidad de conocer que vive en core/.
__all__ = ["RoleEnum", "require_role", "verify_field_access"]


# ──────────────────────────────────────────────
# Jerarquía de roles
# ──────────────────────────────────────────────

# Orden de privilegios: índice mayor = más permisos.
# ADMINISTRADOR puede hacer todo lo que AGRONOMO puede, más lo propio.
_ROLE_HIERARCHY: dict[RoleEnum, int] = {
    RoleEnum.AGRONOMO:      1,
    RoleEnum.ADMINISTRADOR: 2,
}


def _has_minimum_role(user_role: RoleEnum, required_role: RoleEnum) -> bool:
    """Retorna True si user_role tiene al menos el nivel de required_role."""
    return _ROLE_HIERARCHY.get(user_role, 0) >= _ROLE_HIERARCHY.get(required_role, 0)


# ──────────────────────────────────────────────
# require_role — dependencia inyectable de rol
# ──────────────────────────────────────────────

def require_role(minimum_role: RoleEnum) -> Callable:
    """
    Factory que retorna una dependencia FastAPI que exige un rol mínimo.

    Uso en endpoints del API Controller:

        @router.get("/reglas-agroclimaticas")
        async def listar_reglas(
            user: UserContext = Depends(require_role(RoleEnum.ADMINISTRADOR))
        ):
            ...

        @router.get("/parcelas")
        async def listar_parcelas(
            user: UserContext = Depends(require_role(RoleEnum.AGRONOMO))
        ):
            ...

    Parámetros
    ----------
    minimum_role : rol mínimo requerido para acceder al endpoint.

    Retorna
    -------
    El UserContext si el rol es suficiente.

    Lanza
    -----
    InsufficientPermissionsException (403) si el rol no alcanza.
    """

    async def _check_role(
        user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if not _has_minimum_role(user.role, minimum_role):
            logger.warning(
                "Acceso denegado por rol | user=%s | rol_actual=%s | rol_requerido=%s",
                user.user_id,
                user.role.value,
                minimum_role.value,
            )
            raise InsufficientPermissionsException(required_role=minimum_role.value)

        return user

    _check_role.__name__ = f"require_{minimum_role.value}_role"
    return _check_role


# ──────────────────────────────────────────────
# verify_field_access — control a nivel de recurso
# ──────────────────────────────────────────────

def verify_field_access(user: UserContext, campo_id: str) -> None:
    """
    Verifica que el usuario tenga acceso al campo solicitado.

    ADMINISTRADOR: acceso total, sin restricciones.
    AGRONOMO: solo puede operar sobre los campos en su assigned_fields.

    Uso en auth/service.py o en endpoints del API Controller:

        verify_field_access(user, campo_id)
        # si no tiene acceso, lanza ResourceOwnershipException (403)

    Parámetros
    ----------
    user     : contexto del usuario autenticado (viene de get_current_user).
    campo_id : ID del campo que se intenta consultar o modificar.

    Lanza
    -----
    ResourceOwnershipException (403) si el agrónomo no tiene asignado el campo.
    """
    if user.role == RoleEnum.ADMINISTRADOR:
        return  # acceso total

    if campo_id not in user.assigned_fields:
        logger.warning(
            "Acceso denegado por ownership | user=%s | campo_id=%s | campos_asignados_count=%d",
            user.user_id,
            campo_id,
            len(user.assigned_fields),
        )
        raise ResourceOwnershipException(
            details=f"No tenés acceso al campo '{campo_id}'."
        )