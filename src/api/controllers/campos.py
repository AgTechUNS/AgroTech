"""Controller de Campos. Thin: recibe, delega en el Relational Repository y responde."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import (get_relational_repo, get_security_context,
                            requiere_rol, verificar_acceso_campo)
from ..ports import RelationalRepositoryPort, Rol, SecurityContext
from ..schemas import CampoCreate, CampoOut

router = APIRouter(prefix="/campos", tags=["Campos"])


@router.get("", response_model=list[CampoOut])
async def listar_campos(
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    campos = await repo.listar_campos()
    if ctx.es_admin:
        return campos
    return [c for c in campos if c.id in ctx.campos_asignados]


@router.post("", response_model=CampoOut, status_code=201)
async def crear_campo(
    payload: CampoCreate,
    ctx: SecurityContext = Depends(requiere_rol(Rol.ADMINISTRADOR)),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    return await repo.crear_campo(payload.nombre, ctx.user_id)


@router.get("/{campo_id}", response_model=CampoOut)
async def obtener_campo(
    campo_id: str,
    ctx: SecurityContext = Depends(get_security_context),
    repo: RelationalRepositoryPort = Depends(get_relational_repo),
):
    campo = await repo.obtener_campo(campo_id)
    if not campo:
        raise HTTPException(404, "Campo no encontrado.")
    verificar_acceso_campo(ctx, campo_id)
    return campo
