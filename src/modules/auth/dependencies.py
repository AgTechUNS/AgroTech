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
        seeds = [
            ("agronomo@agtech.com", "Juan Agrónomo", "1234567890", "password123", "AGRONOMO"),
            ("test@agtechuns.com", "Admin Test", "1234567890", "12345678", "ADMIN"),
            ("productor@ejemplo.com", "Pedro Productor", "1234567890", "12345678", "PRODUCTOR"),
        ]
        for email, nombre, telefono, pwd, rol in seeds:
            result = await db.execute(
                select(Usuario).where(Usuario.email_usuario == email)
            )
            if result.scalar_one_or_none() is None:
                db.add(Usuario(
                    email_usuario=email, nombre=nombre, telefono=telefono,
                    hash_password=hash_password(pwd), rol=rol,
                ))
        await db.commit()
        logger.info("Seed: %d usuarios de desarrollo creados/verificados", len(seeds))
