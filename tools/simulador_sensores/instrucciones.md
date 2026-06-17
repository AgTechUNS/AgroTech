Para probar
# 0. Activar entorno virtual (siempre desde la raíz del proyecto)
source .venv/bin/activate

# Terminal 1: iniciar broker MQTT
docker compose -f deploy/broker/docker-compose.yml up -d

# Terminal 2: registrar gateways y sensores, iniciar transmisión
python tools/simulador_sensores/lns_console.py

# Terminal 3: procesar los mensajes y guardar en InfluxDB
python -m src.infrastructure.time_series_repo.bootstrap

Dato importante: si no tenés InfluxDB configurado, TimeSeriesRepository va a fallar al conectar. Si solo querés probar el LNS sin la parte de base de datos, podés comentar esa sección o simplemente correr solo lns_console.py y verificar que publique en MQTT.