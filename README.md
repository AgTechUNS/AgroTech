# AgroTech
Plataforma de Monitoreo Agrícola Inteligente

# Estructura Propuesta

El backend de AgTechUNS está construido bajo el patrón arquitectónico de **Monolito Modular** aplicando los principios de *Screaming Architecture*. 

En lugar de organizar el código por capas técnicas (controladores, modelos, servicios), el proyecto se estructura agrupando por **componentes de negocio**, logrando un mapeo 1:1 con nuestros diagramas arquitectónicos C4 (Nivel 3: Componentes).

```text
agtechuns_backend/
├── src/
│   ├── main.py                     # API Controller base (Punto de entrada FastAPI)
│   ├── core/                       # Configuraciones globales (CORS, variables de entorno)
│   │   └── config.py
│   │
│   ├── modules/                    # 📦 MÓDULOS DE NEGOCIO (Dominio)
│   │   │
│   │   ├── security/               # Componente: Security Controller
│   │   │   ├── router.py           # Endpoints de autenticación (/auth)
│   │   │   ├── auth_service.py     # Lógica de JWT y hashing
│   │   │   └── schemas.py          # Pydantic models
│   │   │
│   │   ├── iot_ingestion/          # Componente: IoT Ingestion
│   │   │   ├── mqtt_subscriber.py  # Conexión al broker MQTT
│   │   │   ├── validator.py        # Limpieza de lecturas (Anticorruption)
│   │   │   └── schemas.py
│   │   │
│   │   ├── analytics/              # Componente: Analytics Engine
│   │   │   ├── router.py           # Endpoints de reportes/predicciones
│   │   │   ├── engine.py           # Lógica de procesamiento batch/matemático
│   │   │   └── schemas.py
│   │   │
│   │   ├── external_data/          # Componente: External Data Gateway
│   │   │   ├── open_meteo_client.py# Fetch asíncrono a Open-Meteo
│   │   │   ├── gee_client.py       # Fetch asíncrono a Google Earth Engine
│   │   │   └── mappers.py          # Adaptadores JSON al modelo interno
│   │   │
│   │   └── notifications/          # Componente: Notification Component
│   │       ├── email_sender.py     # Envío de alertas (SMTP/Twilio)
│   │       └── websocket.py        # Push en tiempo real al SPA
│   │
│   └── infrastructure/             # 🗄️ CAPA DE INFRAESTRUCTURA Y PERSISTENCIA
│       │
│       ├── relational_repo/        # Componente: Relational Repository
│       │   ├── database.py         # Conexión a PostgreSQL (SQLAlchemy)
│       │   └── crud.py             # Operaciones SQL puras
│       │
│       └── time_series_repo/       # Componente: Time Series Repository
│           ├── influx_client.py    # Conexión a InfluxDB
│           └── queries.py          # Consultas en lenguaje Flux
│
├── requirements.txt                # Dependencias del proyecto
└── .env                            # Variables de configuración local