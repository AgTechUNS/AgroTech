# Integración del API Controller en `src/main.py`

El módulo se engancha en **una sola línea**, sin tocar el resto del cableado.

```python
# src/main.py
from fastapi import FastAPI
from api import registrar_api          # <-- agregar este import

app = FastAPI(
    title="AgroTech - API",
    description="Sistema de monitoreo agrícola AgTechUNS",
    version="1.1.0",
    lifespan=lifespan,
)

registrar_api(app)                     # <-- agregar esta línea (suma router + middleware PER-02)

# (los include_router existentes pueden quedar; conviven sin conflicto)
app.include_router(external_data_router)
app.include_router(analytics_router)
```

## Cómo correrlo (desde la raíz del repo)

```powershell
uvicorn main:app --reload --app-dir src
```

- Swagger: http://127.0.0.1:8000/docs
- Probar en Swagger: botón **Authorize** y poné el header
  `Authorization: Bearer admin`  (o `Bearer agronomo:c1` para probar RBAC).
