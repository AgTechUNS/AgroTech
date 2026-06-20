"""
get_current_user.py — Interceptor principal del sistema AgTechUNS.

Implementa el patrón "Modo Interceptor" mediante FastAPI Depends().
Se ejecuta antes de que cualquier endpoint protegido reciba la petición.

Flujo:
  1. Extrae el JWT del header Authorization: Bearer <token>
  2. Delega la verificación criptográfica a token_service.decode_token()
  3. Retorna el UserContext al endpoint — sin consultar la base de datos

Cobertura total:
  Al inyectarse como dependencia estructural, ningún endpoint queda
  desprotegido por omisión. El API Controller solo necesita declarar:

      async def mi_endpoint(user: UserContext = Depends(get_current_user)):
          ...

Integración con el API Controller (src/modules/api_controller/):
  El API Controller importa directamente desde este módulo — no hay llamada
  HTTP de por medio. Ambos módulos viven en el mismo proceso FastAPI, por lo
  que el traspaso de control es una llamada a función Python interna:

      # src/modules/api_controller/router.py
      from modules.security.get_current_user import get_current_user
      from modules.security.roles import require_role, verify_field_access
      from modules.security.schemas import UserContext
      from modules.security.core.enums import RoleEnum

      @router.get("/parcelas")
      async def listar_parcelas(user: UserContext = Depends(get_current_user)):
          ...

      @router.get("/reglas")
      async def listar_reglas(user: UserContext = Depends(require_role(RoleEnum.ADMINISTRADOR))):
          ...

Separación de responsabilidades:
  Este archivo solo extrae el token del header y delega.
  La lógica criptográfica vive en token_service.py.
  La lógica de roles vive en roles.py.
"""

import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.security.core.exceptions import InvalidTokenException
from modules.security.schemas import UserContext
from modules.security.token_service import decode_token

logger = logging.getLogger(__name__)

# HTTPBearer extrae automáticamente el token del header
# Authorization: Bearer <token>
# auto_error=False para manejar el 401 con nuestro formato estándar
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserContext:
    """
    Dependencia inyectable que valida el JWT y retorna el UserContext.

    Llamada automáticamente por FastAPI antes de ejecutar cualquier
    endpoint que la declare como dependencia.

    Parámetros
    ----------
    credentials : token extraído del header Authorization por HTTPBearer.
                  None si el header no fue enviado.

    Retorna
    -------
    UserContext con email, rol y campos asignados del usuario autenticado.

    Lanza
    -----
    InvalidTokenException (401) si el header está ausente o el token es inválido.
    TokenExpiredException (401) si el token venció (lanzada por decode_token).

    Uso
    ---
    En cualquier endpoint del API Controller:

        from modules.security.get_current_user import get_current_user
        from modules.security.schemas import UserContext

        @router.get("/parcelas")
        async def listar_parcelas(
            user: UserContext = Depends(get_current_user)
        ):
            # user.user_id, user.role, user.assigned_fields disponibles
            ...
    """
    if credentials is None:
        logger.warning("Evento de seguridad | tipo=MISSING_AUTH_HEADER | detalle=%s", "Header Authorization ausente.")
        raise InvalidTokenException(details="Header Authorization ausente.")

    user_context = decode_token(credentials.credentials)

    logger.debug(
        "Usuario autenticado | user=%s | role=%s",
        user_context.user_id,
        user_context.role.value,
    )

    return user_context