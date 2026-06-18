import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.time_series_repo.influx_client import TimeSeriesRepository
from modules.analytics_engine.router import router as analytics_router
from modules.analytics_engine.tasks import run_batch_diario
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

    async def _ejecutar_batch_diario():
        while True:
            await asyncio.sleep(86400)
            if repo is not None:
                try:
                    resultados = await run_batch_diario(repo)
                    logger.info("Batch diario completado: %d recomendaciones", len(resultados))
                except Exception as e:
                    logger.error("Error en batch diario: %s", e)

    global _tarea_batch
    _tarea_batch = asyncio.create_task(_ejecutar_batch_diario())

    yield

    if _tarea_batch is not None:
        _tarea_batch.cancel()
    if repo is not None:
        await repo.cerrar_conexion()


app = FastAPI(
    title="AgroTech - API",
    description="Sistema de monitoreo agrícola AgTechUNS",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(external_data_router)
app.include_router(analytics_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
