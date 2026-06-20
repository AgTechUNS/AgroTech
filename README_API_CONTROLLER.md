# API Controller — AgTechUNS

Componente de **punto de entrada** del backend. Es un **Thin Controller**:
recibe la petición, **delega** en los componentes (Relational Repository,
Time Series Repository, Analytics Engine) y **responde** en JSON. No calcula
NDVI ni ejecuta SQL: esa lógica vive en los componentes.

Coherente con el ADR de la Entrega 4 (**Monolito Modular** sobre FastAPI):
`api/` es la realización en código del componente "API Controller" del
diagrama C4-Nivel 3, y `main.py` sigue siendo su base (entry point).

## Mapeo documentación -> código

| Responsabilidad (doc) | Dónde se implementa |
| --- | --- |
| Ruteo | `controllers/*.py` (FastAPI `APIRouter`) |
| Validación de entrada (polígono CU-03 / INT-01) | `schemas.py` (`ParcelaCreate`) |
| Delegación en componentes | controllers -> `ports.py` -> adaptadores |
| Filtro de seguridad / RBAC a nivel recurso | `dependencies.py` |
| Traducción de protocolos (JSON) | `response_model` (schemas `*Out`) |
| Rendimiento PER-02 (<= 4 s) | `middleware.py` (`X-Process-Time`) |

## Endpoints <-> Casos de uso

| Método | Ruta | CU |
| --- | --- | --- |
| GET | `/parcelas/{id}/estado` | CU-01 (estado de parcela) |
| POST | `/parcelas` | CU-03 (alta con polígono válido) |
| GET | `/predicciones?parcela_id=` | CU-08 (predicciones) |
| GET | `/reportes?campo_id=` | CU-06 (reporte de campo) |
| GET/POST | `/campos`, `/cultivos`, `/parcelas` | gestión de entidades |

## Puertos y adaptadores (stub -> real)

El controller depende solo de `ports.py`. Hoy se inyectan adaptadores **mock
en memoria** (`adapters_mock.py`) para poder ejecutar y testear sin el resto
del sistema. Para pasar a real, basta cambiar los `get_*` de `dependencies.py`:

| Puerto | Reemplazar por (componente real) |
| --- | --- |
| `RelationalRepositoryPort` | `src/infrastructure/relational_repo` (rama RelationalRepository2, SQLAlchemy/PostgreSQL) |
| `TimeSeriesRepositoryPort` | `src/infrastructure/time_series_repo` (InfluxDB) |
| `AnalyticsEnginePort` | `src/modules/analytics_engine/engine.py` |
| `get_security_context` (stub) | dependencia real del Security Controller (rama Auth-and-Security-Controller, python-jose) |

## Decisiones cerradas

- **SQL:** PostgreSQL (con SQLAlchemy/asyncpg). Resuelve "¿Qué decisión tomamos en cuanto a SQL?".
- Framework: FastAPI · Validación: Pydantic · Docs: OpenAPI/Swagger autogenerado · Protocolo: REST/HTTPS + JSON.

## Notas de coherencia para la doc

- Roles: usar **Administrador / Agrónomo** en todo. El Glosario dice "Agricultor" en RBAC: unificar.
- "PER-02" aparece rotulado como requerimiento *funcional* y de *rendimiento*: dejarlo solo como **no funcional (rendimiento)**.
- `analytics_engine/router.py` ya expone endpoints propios y orquesta directo. Con el API Controller como entrada única, esa lógica debería quedar como funciones del engine (no router), para no tener dos puertas de entrada.
