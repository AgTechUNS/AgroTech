"""
dependencies.py — Dependencias de infraestructura del módulo auth/.

Provee la sesión AsyncSession de SQLAlchemy para inyección
en los endpoints via FastAPI Depends().
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.models import Usuario
from core.config import settings
from modules.security.core.enums import RoleEnum
from modules.security.core.hashing import hash_password

logger = logging.getLogger(__name__)


def build_database() -> Database:
    return Database(dsn=settings.database_dsn, echo=settings.database_echo)


_db = build_database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _db.session() as session:
        yield session


async def init_db() -> None:
    """Crea las tablas y carga el seed de desarrollo."""
    await _db.create_tables()

    import os
    if os.getenv("ENVIRONMENT", "development") != "development":
        return

    async with _db.session_factory() as db:
        seed_users = [
            Usuario(
                email_usuario="agronomo@agtech.com",
                nombre="Juan Agrónomo",
                telefono="1234567890",
                hash_password=hash_password("password123"),
                rol="AGRONOMO",
            ),
            Usuario(
                email_usuario="test@agtechuns.com",
                nombre="Test Admin",
                telefono="1234567890",
                hash_password=hash_password("password123"),
                rol="ADMIN",
            ),
            Usuario(
                email_usuario="productor@ejemplo.com",
                nombre="Productor Ejemplo",
                telefono="1234567890",
                hash_password=hash_password("password123"),
                rol="PRODUCTOR",
            ),
        ]
        for u in seed_users:
            result = await db.execute(
                select(Usuario).where(Usuario.email_usuario == u.email_usuario)
            )
            if result.scalar_one_or_none() is None:
                db.add(u)
                logger.info("Seed: usuario de desarrollo creado | email=%s", u.email_usuario)
        await db.commit()
