"""Controller de Cultivos. Thin: delega en el Relational Repository."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import (get_relational_repo, get_security_context,
                            requiere_rol)
from ..ports import RelationalRepositoryPort, Rol, SecurityContext
from ..schemas import CultivoCreate, CultivoOut

router = APIRouter(prefix="/cultivos", tags=["Cultivos"])


@router.get("", response_model=list[CultivoOut])
async def listar_cultivos(
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    return await repo.listar_cultivos()


@router.post("", response_model=CultivoOut, status_code=201)
async def crear_cultivo(
    payload: CultivoCreate,
    ctx: SecurityContext = Depends(requiere_rol(Rol.ADMINISTRADOR)),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    return await repo.crear_cultivo(payload.nombre)
