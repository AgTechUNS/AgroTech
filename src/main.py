import asyncio
import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI

from core.config import settings
from modules.security.core.exceptions import register_exception_handlers
from modules.security.core.limiter import limiter
from infrastructure.relational_repo.database import Database
from infrastructure.relational_repo.repository import RelationalRepository
from infrastructure.time_series_repo.influx_client import TimeSeriesRepository
from modules.analytics_engine.router import router as analytics_router
from modules.analytics_engine.tasks import run_batch_diario
from modules.auth.router import router as auth_router
from modules.auth.dependencies import init_db
from modules.data_api.router import router as data_api_router
from modules.external_data_gateway.router import router as external_data_router
logger = logging.getLogger(__name__)

_tarea_batch: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    repo: TimeSeriesRepository | None = None
    try:
        repo = await TimeSeriesRepository().initialize()
        logger.info("TimeSeriesRepository conectado exitosamente")
    except Exception as e:
        logger.warning("TimeSeriesRepository no disponible: %s", e)
        repo = None

    app.state.time_series_repo = repo

    db: Database | None = None
    try:
        db = Database(dsn=settings.database_dsn, echo=settings.database_echo)
        await db.create_tables()
        app.state.relational_repo = RelationalRepository(db.session_factory)
        logger.info("Base de datos relacional conectada exitosamente")
        await init_db()
    except Exception as e:
        logger.warning("Base de datos relacional no disponible: %s", e)
        app.state.relational_repo = None

    async def _ejecutar_batch_diario():
        while True:
            await asyncio.sleep(86400)
            if repo is not None:
                try:
                    resultados = await run_batch_diario(repo, relational_repo=app.state.relational_repo)
                    logger.info("Batch diario completado: %d recomendaciones", len(resultados))
                except Exception as e:
                    logger.error("Error en batch diario: %s", e)

    global _tarea_batch
    _tarea_batch = asyncio.create_task(_ejecutar_batch_diario())

    app.state.limiter = limiter

    yield

    if _tarea_batch is not None:
        _tarea_batch.cancel()
    if repo is not None:
        await repo.cerrar_conexion()
    if db is not None:
        await db.close()


app = FastAPI(
    title="AgroTech - API",
    description="Sistema de monitoreo agrícola AgTechUNS",
    version="1.1.0",
    lifespan=lifespan,
)


register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(data_api_router)
app.include_router(external_data_router)
app.include_router(analytics_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
