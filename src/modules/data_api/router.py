import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.relational_repo.models import (
    Alerta, Campo, Cultivo, EjecucionBatch, ImagenSatelital,
    Parcela, ParcelaImagenSatelital, Prediccion, Regla, Sensor, Usuario,
)
from infrastructure.relational_repo.repository import RelationalRepository
from modules.auth.dependencies import get_db
from modules.security.core.enums import RoleEnum
from modules.security.core.hashing import hash_password
from modules.security.get_current_user import get_current_user
from modules.security.schemas import UserContext

# ── Shared base schema ──────────────────────────────

class S(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
    }

# ── Usuario ─────────────────────────────────────────

class UsuarioCreate(S):
    email: EmailStr
    nombre: str = ""
    telefono: str = ""
    password: str = Field(default="password123", min_length=8)
    rol: str = "AGRONOMO"
    admin_email: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_nombre(cls, data: dict) -> dict:
        if not data.get("nombre"):
            email = data.get("email", "")
            data["nombre"] = email.split("@")[0] if isinstance(email, str) and "@" in email else email
        return data

class UsuarioUpdate(S):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[str] = None
    is_active: Optional[bool] = None

class UsuarioOut(S):
    email_usuario: str
    nombre: str
    telefono: str
    rol: str
    is_active: bool
    admin_email: Optional[str] = None
    created_at: datetime

# ── Campo ───────────────────────────────────────────

class CampoCreate(S):
    nombre_campo: str
    coordenadas_campo: str = ""
    descripcion_campo: Optional[str] = None

class CampoUpdate(S):
    coordenadas_campo: Optional[str] = None
    descripcion_campo: Optional[str] = None

class CampoOut(S):
    nombre_campo: str
    coordenadas_campo: str
    descripcion_campo: Optional[str] = None
    admin_email: Optional[str] = None
    created_at: Optional[datetime] = None

# ── Parcela ─────────────────────────────────────────

class ParcelaCreate(S):
    nombre_parcela: str
    coordenadas_parcela: str = ""
    descripcion_parcela: Optional[str] = None
    nombre_campo: str
    nombre_cultivo: Optional[str] = None
    variedad: Optional[str] = None

class ParcelaUpdate(S):
    coordenadas_parcela: Optional[str] = None
    descripcion_parcela: Optional[str] = None
    nombre_cultivo: Optional[str] = None
    variedad: Optional[str] = None

class ParcelaOut(S):
    nombre_parcela: str
    coordenadas_parcela: str
    descripcion_parcela: Optional[str] = None
    nombre_campo: str
    nombre_cultivo: Optional[str] = None
    variedad: Optional[str] = None
    admin_email: Optional[str] = None
    created_at: Optional[datetime] = None

# ── Regla ───────────────────────────────────────────

class ReglaCreate(S):
    nombre: str
    descripcion: Optional[str] = None
    metrica: str
    operador: str
    valor: float
    campos_asignados: list[str] = []

class ReglaUpdate(S):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    metrica: Optional[str] = None
    operador: Optional[str] = None
    valor: Optional[float] = None
    campos_asignados: Optional[list[str]] = None

class ReglaOut(S):
    id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None
    metrica: str
    operador: str
    valor: float
    campos_asignados: list[str]
    admin_email: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("campos_asignados", mode="before")
    @classmethod
    def parse_campos(cls, v: object) -> object:
        if isinstance(v, str):
            return json.loads(v)
        return v

# ── Sensor ──────────────────────────────────────────

class SensorCreate(S):
    device_id: str
    nombre_campo: str
    nombre_parcela: str
    tipo: str = "TH"
    activo: bool = True

class SensorUpdate(S):
    nombre_campo: Optional[str] = None
    nombre_parcela: Optional[str] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None

class SensorOut(S):
    device_id: str
    nombre_campo: str
    nombre_parcela: str
    tipo: str
    activo: bool
    admin_email: Optional[str] = None
    created_at: Optional[datetime] = None

# ── Cultivo ─────────────────────────────────────────

class CultivoCreate(S):
    nombre_cultivo: str
    variedad: str

class CultivoOut(S):
    nombre_cultivo: str
    variedad: str
    admin_email: Optional[str] = None
    created_at: Optional[datetime] = None

class CatalogoCultivoOut(S):
    nombre_cultivo: str
    variedad: str

# ── Router setup ────────────────────────────────────

router = APIRouter(prefix="/api", tags=["Data API"])


def _admin_filter(user: UserContext) -> Optional[str]:
    if user.role == RoleEnum.ADMIN:
        return None
    return user.user_id


async def _repo(db: AsyncSession) -> RelationalRepository:
    from infrastructure.relational_repo.database import Database
    from core.config import settings
    db_inst = Database(dsn=settings.database_dsn, echo=settings.database_echo)
    return RelationalRepository(db_inst.session_factory)


# ── Usuarios ────────────────────────────────────────

@router.get("/usuarios", response_model=list[UsuarioOut])
async def list_usuarios(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Usuario).order_by(Usuario.nombre))
        return list(result.scalars().all())


@router.get("/usuarios/{email}", response_model=UsuarioOut)
async def get_usuario(
    email: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Usuario).where(Usuario.email_usuario == email))
        u = result.scalar_one_or_none()
    if u is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Usuario no encontrado")
    return u


@router.put("/usuarios/{email}", response_model=UsuarioOut)
async def update_usuario(
    email: str, body: UsuarioUpdate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Usuario).where(Usuario.email_usuario == email))
        u = result.scalar_one_or_none()
        if u is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Usuario no encontrado")
        data = body.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(u, k, v)
        await db.flush()
        return u


@router.post("/usuarios", response_model=UsuarioOut, status_code=201)
async def create_usuario(
    body: UsuarioCreate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        existing = await db.execute(
            select(Usuario).where(Usuario.email_usuario == body.email)
        )
        if existing.scalar_one_or_none():
            from fastapi import HTTPException
            raise HTTPException(409, "El usuario ya existe")
        u = Usuario(
            email_usuario=body.email,
            nombre=body.nombre,
            telefono=body.telefono,
            hash_password=hash_password(body.password),
            rol=body.rol,
            admin_email=body.admin_email or user.user_id,
        )
        db.add(u)
        await db.flush()
        return u


# ── Campos ──────────────────────────────────────────

@router.get("/campos", response_model=list[CampoOut])
async def list_campos(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        q = select(Campo).order_by(Campo.nombre_campo)
        result = await db.execute(q)
        return list(result.scalars().all())


@router.post("/campos", response_model=CampoOut, status_code=201)
async def create_campo(
    body: CampoCreate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        c = Campo(**body.model_dump(), admin_email=user.user_id)
        db.add(c)
        await db.flush()
        return c


@router.get("/campos/{nombre_campo}", response_model=CampoOut)
async def get_campo(
    nombre_campo: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Campo).where(Campo.nombre_campo == nombre_campo))
        c = result.scalar_one_or_none()
    if c is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Campo no encontrado")
    return c


@router.put("/campos/{nombre_campo}", response_model=CampoOut)
async def update_campo(
    nombre_campo: str, body: CampoUpdate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Campo).where(Campo.nombre_campo == nombre_campo))
        c = result.scalar_one_or_none()
        if c is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Campo no encontrado")
        for k, v in body.model_dump(exclude_unset=True).items():
            setattr(c, k, v)
        await db.flush()
        return c


@router.delete("/campos/{nombre_campo}", status_code=204)
async def delete_campo(
    nombre_campo: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Campo).where(Campo.nombre_campo == nombre_campo))
        c = result.scalar_one_or_none()
        if c is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Campo no encontrado")
        parcelas = await db.execute(select(Parcela).where(Parcela.nombre_campo == nombre_campo))
        for p in parcelas.scalars():
            await db.delete(p)
        await db.delete(c)


# ── Parcelas ────────────────────────────────────────

@router.get("/campos/{nombre_campo}/parcelas", response_model=list[ParcelaOut])
async def list_parcelas_por_campo(
    nombre_campo: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(Parcela.nombre_campo == nombre_campo).order_by(Parcela.nombre_parcela)
        )
        return list(result.scalars().all())


@router.get("/campos/{nombre_campo}/parcelas/{nombre_parcela}", response_model=ParcelaOut)
async def get_parcela_por_campo(
    nombre_campo: str,
    nombre_parcela: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(
                Parcela.nombre_parcela == nombre_parcela,
                Parcela.nombre_campo == nombre_campo,
            )
        )
        p = result.scalar_one_or_none()
    if p is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Parcela no encontrada")
    return p


@router.put("/campos/{nombre_campo}/parcelas/{nombre_parcela}", response_model=ParcelaOut)
async def update_parcela_por_campo(
    nombre_campo: str,
    nombre_parcela: str,
    body: ParcelaUpdate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(
                Parcela.nombre_parcela == nombre_parcela,
                Parcela.nombre_campo == nombre_campo,
            )
        )
        p = result.scalar_one_or_none()
        if p is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Parcela no encontrada")
        for k, v in body.model_dump(exclude_unset=True).items():
            setattr(p, k, v)
        await db.flush()
        return p


@router.delete("/campos/{nombre_campo}/parcelas/{nombre_parcela}", status_code=204)
async def delete_parcela_por_campo(
    nombre_campo: str,
    nombre_parcela: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(
                Parcela.nombre_parcela == nombre_parcela,
                Parcela.nombre_campo == nombre_campo,
            )
        )
        p = result.scalar_one_or_none()
        if p is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Parcela no encontrada")
        await db.delete(p)


@router.get("/parcelas", response_model=list[ParcelaOut])
async def list_parcelas(
    nombre_campo: Optional[str] = Query(None),
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        q = select(Parcela).order_by(Parcela.nombre_parcela)
        if nombre_campo:
            q = q.where(Parcela.nombre_campo == nombre_campo)
        result = await db.execute(q)
        return list(result.scalars().all())


@router.post("/parcelas", response_model=ParcelaOut, status_code=201)
async def create_parcela(
    body: ParcelaCreate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        p = Parcela(**body.model_dump(), admin_email=user.user_id)
        db.add(p)
        await db.flush()
        return p


@router.get("/parcelas/{nombre_parcela}", response_model=ParcelaOut)
async def get_parcela(
    nombre_parcela: str,
    nombre_campo: str = Query(...),
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(
                Parcela.nombre_parcela == nombre_parcela,
                Parcela.nombre_campo == nombre_campo,
            )
        )
        p = result.scalar_one_or_none()
    if p is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Parcela no encontrada")
    return p


@router.put("/parcelas/{nombre_parcela}", response_model=ParcelaOut)
async def update_parcela(
    nombre_parcela: str, body: ParcelaUpdate,
    nombre_campo: str = Query(...),
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(
                Parcela.nombre_parcela == nombre_parcela,
                Parcela.nombre_campo == nombre_campo,
            )
        )
        p = result.scalar_one_or_none()
        if p is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Parcela no encontrada")
        for k, v in body.model_dump(exclude_unset=True).items():
            setattr(p, k, v)
        await db.flush()
        return p


@router.delete("/parcelas/{nombre_parcela}", status_code=204)
async def delete_parcela(
    nombre_parcela: str,
    nombre_campo: str = Query(...),
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Parcela).where(
                Parcela.nombre_parcela == nombre_parcela,
                Parcela.nombre_campo == nombre_campo,
            )
        )
        p = result.scalar_one_or_none()
        if p is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Parcela no encontrada")
        await db.delete(p)


# ── Reglas ──────────────────────────────────────────

@router.get("/reglas", response_model=list[ReglaOut])
async def list_reglas(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Regla).order_by(Regla.nombre))
        return list(result.scalars().all())


@router.post("/reglas", response_model=ReglaOut, status_code=201)
async def create_regla(
    body: ReglaCreate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        r = Regla(
            id=uuid.uuid4(),
            nombre=body.nombre,
            descripcion=body.descripcion,
            metrica=body.metrica,
            operador=body.operador,
            valor=body.valor,
            campos_asignados=json.dumps(body.campos_asignados),
            admin_email=user.user_id,
        )
        db.add(r)
        await db.flush()
        return r


@router.get("/reglas/{regla_id}", response_model=ReglaOut)
async def get_regla(
    regla_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.get(Regla, regla_id)
    if r is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Regla no encontrada")
    return r


@router.put("/reglas/{regla_id}", response_model=ReglaOut)
async def update_regla(
    regla_id: uuid.UUID, body: ReglaUpdate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        r = await db.get(Regla, regla_id)
        if r is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Regla no encontrada")
        data = body.model_dump(exclude_unset=True)
        if "campos_asignados" in data:
            data["campos_asignados"] = json.dumps(data["campos_asignados"])
        for k, v in data.items():
            setattr(r, k, v)
        await db.flush()
        return r


@router.delete("/reglas/{regla_id}", status_code=204)
async def delete_regla(
    regla_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        r = await db.get(Regla, regla_id)
        if r is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Regla no encontrada")
        await db.delete(r)


# ── Sensores ────────────────────────────────────────

@router.get("/sensores", response_model=list[SensorOut])
async def list_sensores(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Sensor).order_by(Sensor.device_id))
        return list(result.scalars().all())


@router.post("/sensores", response_model=SensorOut, status_code=201)
async def create_sensor(
    body: SensorCreate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        s = Sensor(**body.model_dump(), admin_email=user.user_id)
        db.add(s)
        await db.flush()
        return s


@router.get("/sensores/{device_id}", response_model=SensorOut)
async def get_sensor(
    device_id: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s = await db.get(Sensor, device_id)
    if s is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Sensor no encontrado")
    return s


@router.put("/sensores/{device_id}", response_model=SensorOut)
async def update_sensor(
    device_id: str, body: SensorUpdate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        s = await db.get(Sensor, device_id)
        if s is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Sensor no encontrado")
        for k, v in body.model_dump(exclude_unset=True).items():
            setattr(s, k, v)
        await db.flush()
        return s


@router.delete("/sensores/{device_id}", status_code=204)
async def delete_sensor(
    device_id: str,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        s = await db.get(Sensor, device_id)
        if s is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Sensor no encontrado")
        await db.delete(s)


# ── Cultivos ────────────────────────────────────────

@router.get("/cultivos/catalogo", response_model=list[CatalogoCultivoOut])
async def list_catalogo_cultivos(
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Cultivo.nombre_cultivo, Cultivo.variedad)
            .order_by(Cultivo.nombre_cultivo, Cultivo.variedad)
        )
        return [{"nombre_cultivo": r[0], "variedad": r[1]} for r in result.all()]


@router.get("/cultivos", response_model=list[CultivoOut])
async def list_cultivos(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(select(Cultivo).order_by(Cultivo.nombre_cultivo))
        return list(result.scalars().all())


@router.post("/cultivos", response_model=CultivoOut, status_code=201)
async def create_cultivo(
    body: CultivoCreate,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    existing = await db.execute(
        select(Cultivo).where(
            Cultivo.nombre_cultivo == body.nombre_cultivo,
            Cultivo.variedad == body.variedad,
        )
    )
    if existing.scalar_one_or_none() is not None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe el cultivo '{body.nombre_cultivo}' variedad '{body.variedad}'",
        )
    async with db.begin():
        c = Cultivo(**body.model_dump(), admin_email=user.user_id)
        db.add(c)
        await db.flush()
        return c


@router.delete("/cultivos", status_code=204)
async def delete_cultivo(
    nombre_cultivo: str = Query(...),
    variedad: str = Query(...),
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        from sqlalchemy import select
        result = await db.execute(
            select(Cultivo).where(
                Cultivo.nombre_cultivo == nombre_cultivo,
                Cultivo.variedad == variedad,
            )
        )
        c = result.scalar_one_or_none()
        if c is None:
            from fastapi import HTTPException
            raise HTTPException(404, "Cultivo no encontrado")
        await db.delete(c)
