"""
Publica datos MQTT falsos para probar el pipeline E2E.
Simula un dispositivo LoRaWAN enviando temperatura y humedad.
"""
import json, base64, time, random, os, signal

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("paho-mqtt no instalado. Ejecutá: pip install paho-mqtt")
    exit(1)

BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
DEVICE_ID = "test-device-001"
TOPIC = f"v3/agtechuns-app/devices/{DEVICE_ID}/up"
INTERVAL = 5

BASE_TEMP = 42.0
BASE_HUM = 18.0

running = True

def signal_handler(sig, frame):
    global running
    print("\n[Publisher] Deteniendo...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

print(f"[Publisher] Conectado a {BROKER}:{PORT}")
print(f"[Publisher] Publicando en {TOPIC}")
print(f"[Publisher] Enviando T~{BASE_TEMP}C H~{BASE_HUM}% cada {INTERVAL}s")
print("[Publisher] Presioná Ctrl+C para detener")

n = 0
while running:
    n += 1
    temp = BASE_TEMP + random.uniform(-2, 2)
    hum = BASE_HUM + random.uniform(-3, 3)

    payload = json.dumps({"t": round(temp, 1), "h": round(hum, 1)})
    payload_b64 = base64.b64encode(payload.encode()).decode()

    packet = {
        "end_device_ids": {"device_id": DEVICE_ID},
        "received_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z",
        "uplink_message": {"frm_payload": payload_b64},
        "campo_id": "CampoY",
        "parcela_id": "PY",
    }

    client.publish(TOPIC, json.dumps(packet), qos=1)
    print(f"[{n}] Publicado: T={temp:.1f}C H={hum:.1f}% -> {DEVICE_ID}")
    time.sleep(INTERVAL)

client.loop_stop()
client.disconnect()
print("[Publisher] Detenido.")
