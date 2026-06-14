Para probar
# Terminal 1: iniciar broker MQTT
docker compose -f BrokerMQTT/docker-compose.yml up -d
# Terminal 2: registrar gateways y sensores, iniciar transmisión
python lns_console.py
# Terminal 3: procesar los mensajes y guardar en InfluxDB
python ingestor_repo_connector.py

Dato importante: si no tenés InfluxDB configurado, TimeSeriesRepository va a fallar al conectar. Si solo querés probar el LNS sin la parte de base de datos, podés comentar esa sección o simplemente correr solo lns_console.py y verificar que publique en MQTT.

source mi_entorno(.venv)/bin/activate --> activar el entorno virtual de python en consola