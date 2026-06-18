from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.relational_repo.models import Base


class Database:
    def __init__(self, dsn: str, echo: bool = False):
        connect_args = {}
        if "neon.tech" in dsn.lower():
            connect_args["ssl"] = "require"
        self._engine = create_async_engine(dsn, echo=echo, connect_args=connect_args)
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self):
        await self._engine.dispose()
