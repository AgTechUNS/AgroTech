"""Seed missing users: test@agtechuns.com (ADMIN) and productor@ejemplo.com (PRODUCTOR)."""
import asyncio
import os
import sys

# Ensure src/ is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.models import Usuario
from core.config import settings
from modules.security.core.hashing import hash_password
from sqlalchemy import select


async def main():
    db = Database(dsn=settings.database_dsn, echo=settings.database_echo)
    async with db.session_factory() as session:
        users_to_create = [
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
        for u in users_to_create:
            existing = await session.execute(
                select(Usuario).where(Usuario.email_usuario == u.email_usuario)
            )
            if existing.scalar_one_or_none() is None:
                session.add(u)
                print(f"Created user: {u.email_usuario} ({u.rol})")
            else:
                print(f"User already exists: {u.email_usuario}")
        await session.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
