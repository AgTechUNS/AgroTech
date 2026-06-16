"""
schemas.py — Schemas internos del módulo security/.

Define la forma del contexto de usuario que circula por el sistema
una vez que el Security Controller valida el JWT.

Este contexto es inyectado por FastAPI Depends() en cada endpoint
protegido del API Controller — nunca se construye manualmente.

Inmutabilidad (frozen=True): una vez validado el token y construido
el UserContext, ningún componente posterior puede modificarlo.
"""

from pydantic import Field

from auth.schemas import BaseSchema
from core.enums import RoleEnum


class UserContext(BaseSchema):
    """
    Contexto del usuario autenticado propagado por el Security Controller.

    Construido por security/get_current_user.py a partir del payload JWT.
    Inyectado como dependencia en cualquier endpoint protegido:

        @router.get("/parcelas")
        async def listar_parcelas(user: UserContext = Depends(get_current_user)):
            # user.user_id, user.role, user.assigned_fields disponibles acá
            ...

    Campos
    ------
    user_id         : email_usuario del USUARIO — PK natural del sistema.
    role            : rol asignado (RoleEnum.ADMINISTRADOR o AGRONOMO).
    assigned_fields : IDs de los campos/parcelas a los que tiene acceso.
                      Vacío para ADMINISTRADOR (acceso total).
                      Poblado para AGRONOMO (acceso restringido a sus campos).

    JSON equivalente (si se serializa hacia el cliente):
        {
            "userId": "agronomo@agtech.com",
            "role": "agronomo",
            "assignedFields": ["campo-uuid-1", "campo-uuid-2"]
        }
    """

    model_config = BaseSchema.model_config | {
        "frozen": True,   # inmutable: el contexto no se modifica tras la validación
    }

    user_id: str = Field(
        ...,
        description="email_usuario — identificador único del usuario en el sistema.",
    )
    role: RoleEnum = Field(
        ...,
        description="Rol del usuario. Determina las reglas RBAC aplicables.",
    )
    assigned_fields: list[str] = Field(
        default_factory=list,
        description=(
            "IDs de campos asignados. "
            "Vacío para ADMINISTRADOR (acceso total). "
            "Restringido para AGRONOMO."
        ),
    )