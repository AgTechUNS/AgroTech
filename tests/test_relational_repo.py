import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from sqlalchemy import select

from infrastructure.relational_repo.adapter import SQLAlchemyRelationalRepository
from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.models import CampoModel, UsuarioModel
from modules.relational_repository.dtos import ParcelaCreateDTO


async def main():
    dsn = os.getenv(
        "DATABASE_DSN",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/agrotech",
    )

    print(f"[INFO] Conectando a: {dsn}")
    db = Database(dsn=dsn, echo=True)
    await db.create_tables()
    print("[OK] Tablas creadas")

    repo = SQLAlchemyRelationalRepository(db)

    # ── Cleanup inicial ──────────────────────────────────────────
    async with db.session() as session:
        from sqlalchemy import text
        for tabla in ["reglas", "parcelas", "cultivos", "usuarios", "campos"]:
            await session.execute(text(f"DELETE FROM {tabla}"))
    print("[OK] Limpieza inicial realizada")

    # ── Setup: insertar datos de prueba ──────────────────────────
    async with db.session() as session:
        session.add(CampoModel(
            nombre="campo-test",
            descripcion="Campo de prueba",
            coordenadas='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}',
        ))
        session.add(UsuarioModel(
            email="test@agrotech.com",
            password_hash="abc123",
            rol="AGRONOMO",
        ))
    print("[OK] Datos de prueba insertados (Campo + Usuario)")

    # ── Test 1: crear_parcela ────────────────────────────────────
    parcela_dto = ParcelaCreateDTO(
        nombreParcela="parcela-1",
        nombreCampo="campo-test",
        coordenadasParcela='{"type":"Polygon","coordinates":[[[0,0],[0.5,0],[0.5,0.5],[0,0.5],[0,0]]]}',
        descripcionParcela="Parcela de prueba",
    )
    await repo.crear_parcela(parcela_dto)
    print("[OK] crear_parcela ejecutado sin errores")

    # Verificar que se insertó
    async with db.session() as session:
        result = await session.execute(
            select(CampoModel).where(CampoModel.nombre == "campo-test")
        )
        campo = result.scalar_one()
        print(f"  → Campo verificado: {campo.nombre}, parcelas OK")

    # ── Test 2: obtener_usuario_por_email ────────────────────────
    usuario = await repo.obtener_usuario_por_email("test@agrotech.com")
    assert usuario is not None, "El usuario debería existir"
    assert usuario.email == "test@agrotech.com", "Email no coincide"
    assert usuario.rol == "AGRONOMO", "Rol no coincide"
    print(f"[OK] obtener_usuario_por_email → {usuario.email} ({usuario.rol})")

    # ── Test 3: email inexistente ────────────────────────────────
    no_existe = await repo.obtener_usuario_por_email("no@existe.com")
    assert no_existe is None, "Debería retornar None para email inexistente"
    print("[OK] Email inexistente retorna None")

    # ── Cleanup ──────────────────────────────────────────────────
    async with db.session() as session:
        from sqlalchemy import text
        for tabla in ["reglas", "parcelas", "cultivos", "usuarios", "campos"]:
            await session.execute(text(f"DELETE FROM {tabla}"))
    print("[OK] Datos de prueba limpiados")

    await db.close()
    print("\n✓ Todos los tests pasaron")


if __name__ == "__main__":
    asyncio.run(main())
