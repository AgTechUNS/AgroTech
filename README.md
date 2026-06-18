# AgroTech
Plataforma de Monitoreo Agrícola Inteligente

# Estructura Actual

El backend de AgTechUNS está construido bajo el patrón arquitectónico de **Monolito Modular** aplicando los principios de *Screaming Architecture*.

En lugar de organizar el código por capas técnicas (controladores, modelos, servicios), el proyecto se estructura agrupando por **componentes de negocio**, logrando un mapeo 1:1 con nuestros diagramas arquitectónicos C4 (Nivel 3: Componentes).

```text
AgroTech/
├── src/                                # Código fuente del backend
│   ├── main.py                         # API Controller base (Punto de entrada FastAPI)
│   ├── core/                           # Configuraciones globales
│   │   └── config.py
│   │
│   ├── modules/                        # 📦 MÓDULOS DE NEGOCIO (Dominio)
│   │   │
│   │   ├── iot_ingestion/              # Componente: IoT Ingestion
│   │   │   ├── mqtt_subscriber.py      # Suscriptor MQTT + dedup + workers
│   │   │   ├── schemas.py              # LecturaNormalizada (modelo de dominio)
│   │   │   ├── query_models.py         # TelemetryQuery (especificación de consulta)
│   │   │   └── ports.py                # Puerto: TimeSeriesRepositoryInterface
│   │   │
│   │   ├── analytics_engine/           # Componente: Analytics Engine (TODO)
│   │   │
│   │   ├── external_data_gateway/      # Componente: External Data Gateway
│   │   │   ├── router.py               # Endpoints REST /external-data/*
│   │   │   ├── gateway.py              # Clientes Open-Meteo y Google Earth Engine
│   │   │   ├── models.py               # Pydantic models (WeatherResponse, SatelliteResponse)
│   │   │   └── integration_example.py  # Ejemplo de consumo
│   │   │
│   │   └── security/                   # Componente: Security Controller (TODO)
│   │
│   └── infrastructure/                 # 🗄️ CAPA DE INFRAESTRUCTURA Y PERSISTENCIA
│       │
│       ├── time_series_repo/           # Componente: Time Series Repository
│       │   ├── influx_client.py        # Conexión a InfluxDB + queries Flux
│       │   └── bootstrap.py            # Script de arranque integrado
│       │
│       └── relational_repo/            # Componente: Relational Repository (TODO)
│
├── deploy/                             # Infraestructura de despliegue
│   └── broker/                         # Broker MQTT (Mosquitto)
│       ├── docker-compose.yml
│       └── mosquitto.conf
│
├── tools/                              # Herramientas de desarrollo
│   └── simulador_sensores/             # Simulador LNS (curses TUI)
│       ├── lns_console.py
│       ├── credenciales.env
│       ├── registro_lns.json
│       └── instrucciones.md
│
├── requirements.txt                    # Dependencias del proyecto
├── .env                                # Variables de configuración local
└── .env.example                        # Template de variables de entorno