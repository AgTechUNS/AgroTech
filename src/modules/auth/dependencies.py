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
from infrastructure.relational_repo.models import Campo, Cultivo, Parcela, Regla, Usuario
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

        ]
        for u in seed_users:
            result = await db.execute(
                select(Usuario).where(Usuario.email_usuario == u.email_usuario)
            )
            if result.scalar_one_or_none() is None:
                db.add(u)
                logger.info("Seed: usuario de desarrollo creado | email=%s", u.email_usuario)
        await db.commit()

        admin_email = "test@agtechuns.com"

        # ── Cultivos ─────────────────────────────────────────────────
        seed_cultivos = [
            ("Trigo", "ACA 303"), ("Trigo", "Baguette 601"), ("Trigo", "MS INTA 119"),
            ("Maíz", "DK 390"), ("Maíz", "P 2089"), ("Maíz", "AX 7761"),
            ("Soja", "DM 60i"), ("Soja", "NS 4611"), ("Soja", "DM 40R"),
            ("Girasol", "Aguará 6"), ("Girasol", "Pan 7001"), ("Girasol", "ACA 885"),
            ("Cebada", "Scarlett"), ("Cebada", "Explorer"), ("Cebada", "Andreia"),
            ("Avena", "Cristal"), ("Avena", "INIA 910"), ("Avena", "Margot"),
            ("Sorgo", "ACA 558"), ("Sorgo", "INTA 15"), ("Sorgo", "Caburé"),
        ]
        for nombre_cultivo, variedad in seed_cultivos:
            result = await db.execute(
                select(Cultivo).where(
                    Cultivo.nombre_cultivo == nombre_cultivo,
                    Cultivo.variedad == variedad,
                )
            )
            if result.scalar_one_or_none() is None:
                db.add(Cultivo(nombre_cultivo=nombre_cultivo, variedad=variedad, admin_email=admin_email))
        logger.info("Seed: cultivos creados (%d entradas)", len(seed_cultivos))

        # ── Campos ───────────────────────────────────────────────────
        import json
        seed_campos = [
            {
                "nombre_campo": "Campo Norte",
                "descripcion_campo": "Campo de prueba ubicado al norte",
                "coordenadas_campo": json.dumps({
                    "type": "Polygon",
                    "coordinates": [[[-62.5, -38.7], [-62.3, -38.7], [-62.3, -38.9], [-62.5, -38.9], [-62.5, -38.7]]]
                }),
            },
            {
                "nombre_campo": "Campo Sur",
                "descripcion_campo": "Campo de prueba ubicado al sur",
                "coordenadas_campo": json.dumps({
                    "type": "Polygon",
                    "coordinates": [[[-62.8, -39.0], [-62.6, -39.0], [-62.6, -39.2], [-62.8, -39.2], [-62.8, -39.0]]]
                }),
            },
        ]
        for c in seed_campos:
            result = await db.execute(select(Campo).where(Campo.nombre_campo == c["nombre_campo"]))
            if result.scalar_one_or_none() is None:
                db.add(Campo(nombre_campo=c["nombre_campo"], descripcion_campo=c["descripcion_campo"],
                             coordenadas_campo=c["coordenadas_campo"], admin_email=admin_email))
        logger.info("Seed: campos creados (%d entradas)", len(seed_campos))

        # ── Parcelas ─────────────────────────────────────────────────
        seed_parcelas = [
            {"nombre_parcela": "Lote A", "nombre_campo": "Campo Norte", "nombre_cultivo": "Trigo", "variedad": "ACA 303",
             "descripcion_parcela": "Lote A - Trigo ACA 303",
             "coordenadas_parcela": json.dumps({
                 "type": "Polygon",
                 "coordinates": [[[-62.45, -38.75], [-62.38, -38.75], [-62.38, -38.82], [-62.45, -38.82], [-62.45, -38.75]]]
             })},
            {"nombre_parcela": "Lote B", "nombre_campo": "Campo Norte", "nombre_cultivo": "Soja", "variedad": "DM 60i",
             "descripcion_parcela": "Lote B - Soja DM 60i",
             "coordenadas_parcela": json.dumps({
                 "type": "Polygon",
                 "coordinates": [[[-62.38, -38.75], [-62.30, -38.75], [-62.30, -38.82], [-62.38, -38.82], [-62.38, -38.75]]]
             })},
            {"nombre_parcela": "Lote A", "nombre_campo": "Campo Sur", "nombre_cultivo": "Maíz", "variedad": "DK 390",
             "descripcion_parcela": "Lote A - Maíz DK 390",
             "coordenadas_parcela": json.dumps({
                 "type": "Polygon",
                 "coordinates": [[[-62.75, -39.05], [-62.68, -39.05], [-62.68, -39.12], [-62.75, -39.12], [-62.75, -39.05]]]
             })},
            {"nombre_parcela": "Lote B", "nombre_campo": "Campo Sur", "nombre_cultivo": "Girasol", "variedad": "Aguará 6",
             "descripcion_parcela": "Lote B - Girasol Aguará 6",
             "coordenadas_parcela": json.dumps({
                 "type": "Polygon",
                 "coordinates": [[[-62.68, -39.05], [-62.60, -39.05], [-62.60, -39.12], [-62.68, -39.12], [-62.68, -39.05]]]
             })},
        ]
        for p in seed_parcelas:
            result = await db.execute(
                select(Parcela).where(
                    Parcela.nombre_parcela == p["nombre_parcela"],
                    Parcela.nombre_campo == p["nombre_campo"],
                )
            )
            if result.scalar_one_or_none() is None:
                db.add(Parcela(**p, admin_email=admin_email))
        logger.info("Seed: parcelas creadas (%d entradas)", len(seed_parcelas))

        # ── Reglas ───────────────────────────────────────────────────
        import uuid
        seed_reglas = [
            {
                "id": uuid.uuid4(),
                "nombre": "Alerta Calor Extremo",
                "descripcion": "Temperatura excesiva que puede dañar los cultivos",
                "metrica": "temperatura",
                "operador": ">",
                "valor": 35.0,
                "campos_asignados": json.dumps(["Campo Norte", "Campo Sur"]),
            },
            {
                "id": uuid.uuid4(),
                "nombre": "Alerta Helada",
                "descripcion": "Temperatura bajo cero con riesgo de helada",
                "metrica": "temperatura",
                "operador": "<",
                "valor": 0.0,
                "campos_asignados": json.dumps(["Campo Norte", "Campo Sur"]),
            },
            {
                "id": uuid.uuid4(),
                "nombre": "Estrés Hídrico",
                "descripcion": "Humedad del suelo por debajo del nivel óptimo",
                "metrica": "humedad",
                "operador": "<",
                "valor": 30.0,
                "campos_asignados": json.dumps(["Campo Norte", "Campo Sur"]),
            },
        ]
        for r in seed_reglas:
            result = await db.execute(select(Regla).where(Regla.nombre == r["nombre"]))
            if result.scalar_one_or_none() is None:
                db.add(Regla(**r, admin_email=admin_email))
        logger.info("Seed: reglas creadas (%d entradas)", len(seed_reglas))

        await db.commit()
        logger.info("Seed de desarrollo completado")
