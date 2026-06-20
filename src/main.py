from fastapi import FastAPI

from modules.external_data_gateway.router import router as external_data_router

app = FastAPI(
    title="AgroTech - External Data Gateway",
    description="Capa de Anticorrupción para consumo de APIs externas (Open-Meteo, Google Earth Engine)",
    version="1.0.0",
)

app.include_router(external_data_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
