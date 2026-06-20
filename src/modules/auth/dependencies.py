"""
dependencies.py — Dependencias de infraestructura del módulo auth/.

Provee la sesión AsyncSession de SQLAlchemy para inyección
en los endpoints via FastAPI Depends(), e inicialización de la base de datos
al arranque de la app.
"""

import logging
import uuid
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from modules.security.core.config import get_settings
from modules.security.core.enums import RoleEnum
from modules.security.core.hashing import hash_password

logger = logging.getLogger(__name__)


def _build_engine():
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL.get_secret_value(),
        echo=settings.ENVIRONMENT == "development",
        pool_pre_ping=True,
    )


_engine       = _build_engine()
_SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia que provee una sesión de base de datos por request.

    Uso en endpoints:
        async def mi_endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with _SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Crea las tablas y carga el seed de desarrollo si ENVIRONMENT=development.

    Llamar una sola vez desde el lifespan de la app.
    """
    from modules.auth.models import Base, Usuario, UsuarioRolCampo

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if get_settings().ENVIRONMENT != "development":
        return

    async with _SessionLocal() as db:
        result = await db.execute(
            select(Usuario).where(Usuario.email_usuario == "agronomo@agtech.com")
        )
        if result.scalar_one_or_none() is None:
            usuario = Usuario(
                email_usuario="agronomo@agtech.com",
                nombre="Juan Agrónomo",
                telefono="1234567890",
                hash_password=hash_password("password123"),
            )
            campo_id = uuid.uuid4()
            rol = UsuarioRolCampo(
                email_usuario="agronomo@agtech.com",
                rol=RoleEnum.AGRONOMO,
                campo_id=campo_id,
            )
            db.add(usuario)
            db.add(rol)
            await db.commit()
            logger.info("Seed: usuario de desarrollo creado | email=agronomo@agtech.com")