# AgroTech
Plataforma de Monitoreo Agrícola Inteligente

## Estructura del Proyecto

El proyecto combina un **backend en Python/FastAPI** (monolito modular) con un **frontend SPA en Next.js** (agtech-spa).

### Backend (`src/`)

Construido bajo el patrón de **Monolito Modular** con *Screaming Architecture*: el código se organiza por componentes de negocio en lugar de capas técnicas, logrando un mapeo 1:1 con los diagramas C4 (Nivel 3: Componentes).

```text
src/
├── main.py                         # API Controller base (Punto de entrada FastAPI)
├── core/                           # Configuraciones globales
│   └── config.py
│
├── modules/                        # MÓDULOS DE NEGOCIO (Dominio)
│   ├── auth/                       # Componente: Authentication Controller
│   │   ├── router.py               # Endpoints POST /auth/login, /refresh, /reset-*
│   │   ├── service.py              # Lógica: login, refresh, reset de contraseña
│   │   ├── models.py               # ORM SQLAlchemy: Usuario, UsuarioRolCampo
│   │   ├── schemas.py              # Pydantic: LoginRequest, TokenResponse, BaseSchema…
│   │   └── dependencies.py         # get_db(): sesión AsyncSession por request
│   │
│   ├── security/                   # Componente: Security Controller
│   │   ├── get_current_user.py     # Dependencia FastAPI: extrae y valida el JWT
│   │   ├── roles.py                # RBAC: require_role(), verify_field_access()
│   │   ├── token_service.py        # JWT: create_access_token/refresh, decode_token
│   │   ├── schemas.py              # UserContext (contexto del usuario autenticado)
│   │   └── core/                   # Núcleo interno del componente
│   │       ├── config.py           # Settings (SECRET_KEY, algoritmo, TTLs)
│   │       ├── enums.py            # RoleEnum: ADMINISTRADOR, AGRONOMO
│   │       ├── exceptions.py       # Excepciones de negocio + handlers globales
│   │       ├── hashing.py          # bcrypt: hash_password, verify_password
│   │       └── limiter.py          # Instancia slowapi (rate limiting)
│   │
│   ├── iot_ingestion/              # Componente: IoT Ingestion
│   │   ├── mqtt_subscriber.py      # Suscriptor MQTT + dedup + workers
│   │   ├── schemas.py              # LecturaNormalizada (modelo de dominio)
│   │   ├── query_models.py         # TelemetryQuery (especificación de consulta)
│   │   └── ports.py                # Puerto: TimeSeriesRepositoryInterface
│   │
│   ├── analytics_engine/           # Componente: Analytics Engine
│   │
│   └── external_data_gateway/      # Componente: External Data Gateway
│       ├── router.py               # Endpoints REST /external-data/*
│       ├── gateway.py              # Clientes Open-Meteo y Google Earth Engine
│       ├── models.py               # Pydantic models
│       └── integration_example.py
│
└── infrastructure/                 # CAPA DE INFRAESTRUCTURA Y PERSISTENCIA
    ├── time_series_repo/           # Componente: Time Series Repository
    │   ├── influx_client.py        # Conexión a InfluxDB + queries Flux
    │   └── bootstrap.py
    │
    └── relational_repo/            # Componente: Relational Repository (TODO)
```

### Frontend SPA (`agtech-spa/`)

Aplicación web autónoma construida con **Next.js 14** (App Router), **React 18** y **TypeScript**. Sirve como interfaz de usuario para la gestión de campos, cultivos, parcelas y reglas.

```text
agtech-spa/
├── app/                            # Next.js App Router
│   ├── page.tsx                    # Dashboard home
│   ├── login/page.tsx              # Login
│   ├── reset-password/page.tsx     # Reset password
│   ├── campos/                     # Módulo Campos
│   │   ├── page.tsx                #   Listado + mapa
│   │   ├── crear/page.tsx          #   Crear campo con polígono
│   │   └── [nombreCampo]/          #   Detalle de campo
│   │       ├── page.tsx            #     Parcelas + mapa
│   │       └── parcelas/crear/page.tsx  # Crear parcela
│   ├── cultivos/                   # Módulo Cultivos
│   │   ├── page.tsx                #   Listado
│   │   └── crear/page.tsx          #   Crear cultivo
│   ├── reglas/                     # Módulo Reglas
│   │   ├── page.tsx                #   Listado
│   │   └── crear/page.tsx          #   Crear regla
│   └── api/                        # API Routes (BFF)
│       ├── campos/route.ts
│       ├── cultivos/route.ts
│       ├── reglas/route.ts
│       └── campos/[nombreCampo]/parcelas/route.ts
│
├── components/                     # Componentes React
│   ├── ui/                         #   UI Kit (Button, Input, Card, Table, Spinner)
│   ├── layout/                     #   Sidebar, DashboardLayout
│   └── map/                        #   MapSelector, FieldsMap, DrawControl (Leaflet)
│
├── contexts/                       # AuthContext (estado global de autenticación)
├── hooks/                          # useAuth (login/logout/refresh con mock)
├── lib/                            # Lógica compartida
│   ├── data/                       #   store.ts (lectura/escritura JSON) + seed.ts
│   ├── services/                   #   Servicios HTTP a API Routes
│   └── types.ts                    #   Tipos compartidos
│
├── .data/                          # Persistencia local (gitignored)
├── .env.local                      # NEXT_PUBLIC_MOCK_AUTH=true, BACKEND_URL=
└── package.json                    # Dependencias: Next.js, React, Leaflet, recharts
```

**Arquitectura de datos (SPA):**
- Las API Routes de Next.js actúan como **BFF** (Backend For Frontend)
- Actualmente persisten en archivos JSON bajo `.data/` (gitignored)
- Cuando el Relational Repository esté disponible, las API Routes swichearán a `fetch(BACKEND_URL)`
- Login mock activo con `NEXT_PUBLIC_MOCK_AUTH=true` (usuario: `test@agtechuns.com` / `12345678`)

## Requisitos

| Componente | Requisito |
|------------|-----------|
| Backend    | Python 3.11+, FastAPI, dependencias en `requirements.txt` |
| Frontend   | Node.js 18+, npm, dependencias en `agtech-spa/package.json` |
| Broker     | Docker (para Mosquitto MQTT) |

## Inicio Rápido

### Backend
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Frontend SPA
```bash
cd agtech-spa
npm install
npm run dev                # http://localhost:3000
```

## Despliegue

```text
deploy/
└── broker/                         # Broker MQTT (Mosquitto)
    ├── docker-compose.yml
    └── mosquitto.conf
```

## Herramientas

```text
tools/
└── simulador_sensores/             # Simulador LNS (curses TUI)
    ├── lns_console.py
    ├── credenciales.env
    ├── registro_lns.json
    └── instrucciones.md
```

## Variables de Entorno

| Variable | Descripción | ¿Obligatoria? |
|----------|-------------|---------------|
| `DATABASE_URL` | URL de base de datos relacional | No (mock por ahora) |
| `INFLUXDB_URL` | URL de InfluxDB | Solo para time-series |
| `BACKEND_URL` | URL del backend para API Routes del SPA | No (usa JSON store por ahora) |
| `NEXT_PUBLIC_MOCK_AUTH` | Habilita mock de autenticación en SPA | Solo SPA |
