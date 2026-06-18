import asyncio
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from hashlib import sha256

from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.models import (
    CampoModel, CultivoModel, ParcelaModel, ReglaModel, UsuarioModel,
)


async def main():
    dsn = os.getenv("DATABASE_DSN", "postgresql+asyncpg://postgres:postgres@localhost:5432/agrotech")
    db = Database(dsn=dsn, echo=False)
    await db.create_tables()
    print("[OK] Tablas creadas")

    # ── Limpiar datos existentes ────────────────────────────────
    async with db.session() as session:
        for tabla in ["reglas", "parcelas", "cultivos", "usuarios", "campos"]:
            await session.execute(text(f"DELETE FROM {tabla}"))
    print("[OK] Limpieza realizada")

    # ── Usuarios ────────────────────────────────────────────────
    def _hash(pw: str) -> str:
        return sha256(pw.encode()).hexdigest()

    usuarios = [
        UsuarioModel(email="admin@agrotech.com", password_hash=_hash("admin123"), rol="ADMIN"),
        UsuarioModel(email="agronomo@agrotech.com", password_hash=_hash("campo2024"), rol="AGRONOMO"),
        UsuarioModel(email="productor@agrotech.com", password_hash=_hash("cosecha2024"), rol="PRODUCTOR"),
    ]
    async with db.session() as session:
        for u in usuarios:
            session.add(u)
    print("[OK] 3 usuarios creados")

    # ── Cultivos ────────────────────────────────────────────────
    cultivos = [
        CultivoModel(nombre="Trigo", umbral_humedad_minima=30.0, umbral_temperatura_maxima=35.0),
        CultivoModel(nombre="Maíz", umbral_humedad_minima=40.0, umbral_temperatura_maxima=38.0),
        CultivoModel(nombre="Soja", umbral_humedad_minima=35.0, umbral_temperatura_maxima=36.0),
        CultivoModel(nombre="Girasol", umbral_humedad_minima=25.0, umbral_temperatura_maxima=40.0),
    ]
    async with db.session() as session:
        for c in cultivos:
            session.add(c)
    print("[OK] 4 cultivos creados")

    # ── Campos ──────────────────────────────────────────────────
    campos = [
        CampoModel(
            nombre="Campo Los Pinos",
            descripcion="Establecimiento norte destinado a cultivos rotativos",
            coordenadas='{"type":"Polygon","coordinates":[[[-62.5,-38.0],[-62.3,-38.0],[-62.3,-38.2],[-62.5,-38.2],[-62.5,-38.0]]]}',
        ),
        CampoModel(
            nombre="Campo El Ombú",
            descripcion="Campo sur con riego por goteo",
            coordenadas='{"type":"Polygon","coordinates":[[[-62.8,-38.5],[-62.6,-38.5],[-62.6,-38.7],[-62.8,-38.7],[-62.8,-38.5]]]}',
        ),
    ]
    async with db.session() as session:
        for c in campos:
            session.add(c)
    print("[OK] 2 campos creados")

    # ── Parcelas ────────────────────────────────────────────────
    parcelas = [
        ParcelaModel(nombre="Lote A", campo_nombre="Campo Los Pinos", coordenadas='{"type":"Polygon","coordinates":[[[-62.5,-38.0],[-62.4,-38.0],[-62.4,-38.1],[-62.5,-38.1],[-62.5,-38.0]]]}', descripcion="Lote de trigo", cultivo_nombre="Trigo"),
        ParcelaModel(nombre="Lote B", campo_nombre="Campo Los Pinos", coordenadas='{"type":"Polygon","coordinates":[[[-62.4,-38.0],[-62.3,-38.0],[-62.3,-38.1],[-62.4,-38.1],[-62.4,-38.0]]]}', descripcion="Lote de maíz", cultivo_nombre="Maíz"),
        ParcelaModel(nombre="Lote C", campo_nombre="Campo Los Pinos", coordenadas='{"type":"Polygon","coordinates":[[[-62.5,-38.1],[-62.4,-38.1],[-62.4,-38.2],[-62.5,-38.2],[-62.5,-38.1]]]}', descripcion="Lote de soja", cultivo_nombre="Soja"),
        ParcelaModel(nombre="Lote 1", campo_nombre="Campo El Ombú", coordenadas='{"type":"Polygon","coordinates":[[[-62.8,-38.5],[-62.7,-38.5],[-62.7,-38.6],[-62.8,-38.6],[-62.8,-38.5]]]}', descripcion="Lote de girasol", cultivo_nombre="Girasol"),
        ParcelaModel(nombre="Lote 2", campo_nombre="Campo El Ombú", coordenadas='{"type":"Polygon","coordinates":[[[-62.7,-38.5],[-62.6,-38.5],[-62.6,-38.6],[-62.7,-38.6],[-62.7,-38.5]]]}', descripcion="Lote de trigo", cultivo_nombre="Trigo"),
    ]
    async with db.session() as session:
        for p in parcelas:
            session.add(p)
    print("[OK] 5 parcelas creadas")

    # ── Reglas ──────────────────────────────────────────────────
    reglas = [
        ReglaModel(metrica="temperatura", operador=">=", valor=38.0),
        ReglaModel(metrica="humedad", operador="<", valor=20.0),
        ReglaModel(metrica="ndvi", operador="<", valor=0.3),
    ]
    async with db.session() as session:
        for r in reglas:
            session.add(r)
    print("[OK] 3 reglas creadas")

    await db.close()
    print("\n✓ Seed completado. Datos disponibles para desarrollo.")


if __name__ == "__main__":
    asyncio.run(main())
