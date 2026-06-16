"""
dependencies.py — Dependencias de infraestructura del módulo auth/.

Provee la sesión AsyncSession de SQLAlchemy para inyección
en los endpoints via FastAPI Depends().
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings


def _build_engine():
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL.get_secret_value(),
        echo=settings.ENVIRONMENT == "development",
        pool_pre_ping=True,
    )


_engine        = _build_engine()
_SessionLocal  = async_sessionmaker(_engine, expire_on_commit=False)


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